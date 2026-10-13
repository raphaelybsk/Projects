package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/fs"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

// --- data structures ---

// detection rule: name, severity and regular expression
type Rule struct {
	Name string
	Severity string
	Regex *regexp.Regexp
}

// Finding represents a possible secret found
type Finding struct {
	Type string `json:"type"`
	Severity string `json:"severity"`
	File string `json:"file"`
	Line int `json:"line"`
	Match string `json:"match"`
	Commit string `json:"commit,omitempty"` // only on git found history
	Author string `json:"author,omitempty"` // only on git found history
}

// Report stored in JSON file
type Report struct {
	Total int `json:"total"`
	Findings []Finding `json:"findings"`
}

// --- Configuration ---

// rules list
// if regex has a group in parenthesis, only this group is treated as the secret ???
// Se a regex tiver um grupo entre parênteses (...), só esse grupo é tratado como o segredo ???
var rules = []Rule{
	{"AWS Access Key", "HIGH", regexp.MustCompile(`AKIA[0-9A-Z]{16}`)},
	{"GitHub Token", "HIGH", regexp.MustCompile(`gh[pousr]_[A-Za-z0-9]{36,}`)},
	{"Private Key", "HIGH", regexp.MustCompile(`-----BEGIN [A-Z ]*PRIVATE KEY-----`)},
	{"Password in config", "MEDIUM", regexp.MustCompile(`(?i)(?:password|passwd|pwd|secret|api_?key|token)\s*[:=]\s*["']?([^\s"']{8,})`)},
}

// possible words for entropy analysis: long sequencies of letters, numbers and base64 symbols
var wordRegex = regexp.MustCompile(`[A-Za-z0-9+/=_-]{20,}`)

// folders not worth analysing
var skipDirs = map[string]bool{
	".git": true, "node_modules": true, "vendor": true, ".venv": true,
}

// automatically generated files (lots of hashes and false positives) ???
var skipFiles = map[string]bool{
	"go.sum": true, "package-lock.json": true, "yarn.lock": true,
	"pnpm-lock.yaml": true, "Cargo.lock": true, "poetry.lock": true,
}

const maxFileSize = 1024 * 1024 // ignore files over 1 MB -- why???

// --- auxiliary functions ---

// entropy calculates the Shannon entropy of a text
// the more random the text, the bigger the value (normal text: under ~4 - random keys: above ~4.5)
func entropy(s string) float64 {
	counts := map[rune]float64{}
	for _, c := range s {
		counts[c]++
	}
	total := float64(len(s))
	result := 0.0
	for _, n := range counts {
		p := n / total // probability of each character
		result -= p * math.Log2(p)
	}
	return result
}

// mask hides the secret so the report won't reveal it
func mask(s string) string {
	if len(s) >= 20 {
		// long secrets: shows the first and last 4 characters
		return s[:4] + strings.Repeat("*", len(s)-8) + s[len(s)-4:]
	}
	if len(s) > 2 {
		// short secrets: shows only the first 2 characters
		return s[:2] + strings.Repeat("*", len(s)-2)
	}
	return strings.Repeat("*", len(s))
}

// skipFile used to know if a file should be ignored by the name or by the folder ???
func skipFile(path string) bool {
	if skipFiles[filepath.Base(path)] || strings.HasSuffix(path, ".lock") {
		return true
	}
	for dir := range skipDirs {
		if strings.Contains(path, dir+"/") {
			return true
		}
	}
	return false
}

// --- detection engine ---

// scanLine analyses ONE text line and returns the findings ???
// used both in current files and history git 
func scanLine(line string, file string, lineNo int) []Finding {
	var found []Finding

	// 1- rules (regex)
	for _, rule := range rules {
		m := rule.Regex.FindStringSubmatch(line)
		if m == nil {
			continue // this rule didn't catch anything ???
		}
		secret := m[0] // m[0] is all the text the regex caught ???
		if len(m) > 1 {
			secret = m[1] // m[1] is the group in parenthesis if it exists ???
		}
		found = append(found, Finding{
			Type: rule.Name, Severity: rule.Severity,
			File: file, Line: lineNo, Match: mask(secret),
		})
		break // the most specific rules come first: one line generates only one finding ???
	}

	// 2 - entropy: only if none of the rules caught this line (avoids duplicate findings)
	if len(found) == 0 {
		for _, word := range wordRegex.FindAllString(line, -1) {
			if entropy(word) > 4.5 {
				found = append(found, Finding{
					Type: "High-entropy string", Severity: "MEDIUM",
					File: file, Line: lineNo, Match: mask(word),
				})
			}
		}
	}
	return found
}

// scanFile reads a file and analyses each line
func scanFile(path string) []Finding {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil // ignore if we cannot read it
	}

	// Binary file? Look for a 0 byte in the first 8000 bytes
	head := data
	if len(head) > 8000 {
		head = head[:8000]
	}
	if bytes.IndexByte(head, 0) != -1 {
		return nil
	}

	var all []Finding
	for i, line := range strings.Split(string(data), "\n") {
		all = append(all, scanLine(line, path, i+1)...) // i+1 because the lines start at 1
	}
	return all
}

// scanDirectory goes through the folder and analyses all the files 
func scanDirectory(root string) []Finding {
	var all []Finding

	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return nil // ignore and continue if we have no access to this item
		}
		if d.IsDir() {
			if skipDirs[d.Name()] {
				return filepath.SkipDir // skip the whole folder 
			}
			return nil
		}
		if skipFile(path) {
			return nil
		}
		info, err := d.Info()
		if err != nil || info.Size() > maxFileSize {
			return nil
		}
		all = append(all, scanFile(path)...)
		return nil
	})
	if err != nil {
		fmt.Println("Error traversing the folder:", err)
	}
	return all
}

// --- Git history ---

// recognise block headers like "@@ -10,6 +12,8 @@" and extracts the number 12
var hunkRegex = regexp.MustCompile(`^@@ -\d+(?:,\d+)? \+(\d+)`)

// scanGitHistory runs "git log -p" and analyses the added lines in each commit
func scanGitHistory(root string) []Finding {
	cmd := exec.Command("git", "-C", root, "log", "-p", "--all", "--no-color",
		"--pretty=format:COMMIT:%h|%an") // one line "COMMIT:hash|autor" before each diff
	out, err := cmd.Output()
	if err != nil {
		fmt.Println("Warning: it was not possible to read the Git history:", err)
		return nil
	}

	var all []Finding
	commit, author, file := "", "", ""
	lineNo := 0

	for _, line := range strings.Split(string(out), "\n") {
		switch {
		case strings.HasPrefix(line, "COMMIT:"):
			// new commit: stores the hash and the author
			parts := strings.SplitN(strings.TrimPrefix(line, "COMMIT:"), "|", 2)
			commit = parts[0]
			author = ""
			if len(parts) > 1 {
				author = parts[1]
			}
			file = ""

		case strings.HasPrefix(line, "+++ "):
			// new file inside the commit: "+++ b/path/file"
			file = strings.TrimPrefix(line, "+++ b/")
			if line == "+++ /dev/null" {
				file = "" // deleted file: nothing to analyse
			}

		case strings.HasPrefix(line, "@@"):
			// new block of changes: finds out the line where it begins
			m := hunkRegex.FindStringSubmatch(line)
			if m != nil {
				n, _ := strconv.Atoi(m[1])
				lineNo = n - 1 // the counter increments 1 before each line
			}

		case file == "" || skipFile(file):
			// ignore useless file

		case strings.HasPrefix(line, "+"):
			// ADDED line in this commit: here's where we look for secrets
			lineNo++
			found := scanLine(line[1:], file, lineNo) // line[1:] removes "+"
			for i := range found {
				found[i].Commit = commit
				found[i].Author = author
			}
			all = append(all, found...)

		case strings.HasPrefix(line, " "):
			lineNo++ // context line (not changed): just increments the counter
		}
		// lines that start by "-" (removed) don't exist in the new file: ignore it
	}
	return all
}

// --- Reports ---

func printReport(findings []Finding) {
	fmt.Println("=== SECRETS REPORT ===")
	fmt.Println()
	for _, f := range findings {
		line := fmt.Sprintf("[%s] %s — %s:%d (%s)", f.Severity, f.Type, f.File, f.Line, f.Match)
		if f.Commit != "" {
			line += fmt.Sprintf(" [commit %s, author %s]", f.Commit, f.Author)
		}
		fmt.Println(line)
	}
	fmt.Println()
	fmt.Printf("%d potential secrets found.\n", len(findings))
}

func saveJSON(filename string, findings []Finding) {
	if findings == nil {
		findings = []Finding{} // "[]" instead of "null" in JSON
	}
	report := Report{Total: len(findings), Findings: findings}

	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		fmt.Println("Error generating the JSON file:", err)
		return
	}
	err = os.WriteFile(filename, data, 0644)
	if err != nil {
		fmt.Println("Error storing the file:", err)
		return
	}
	fmt.Println("Report saved to", filename)
}

// --- main ---

func main() {
	// command line flags: name, value by default, description
	path := flag.String("path", ".", "analysing folder")
	useGit := flag.Bool("git", false, "also analyse Git history")
	jsonFile := flag.String("json", "", "store the report in this JSON file")
	flag.Parse()

	if _, err := os.Stat(*path); err != nil {
		fmt.Println("Error: the folder doesn't exist:", *path)
		os.Exit(1)
	}

	findings := scanDirectory(*path)
	if *useGit {
		findings = append(findings, scanGitHistory(*path)...)
	}

	printReport(findings)

	if *jsonFile != "" {
		saveJSON(*jsonFile, findings)
	}
}