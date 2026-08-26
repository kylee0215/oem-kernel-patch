#!/usr/bin/env python3
"""
Check if commits have been sent to kernel-team mailing list

Fetches the thread.html index page from kernel-team mailing list archives
and checks if commit subjects from unlanded commits appear in the email subjects.
Can output as text report or enhanced HTML.
"""

import sys
import re
import logging
import urllib.request
from html import unescape
import argparse
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

logger = logging.getLogger(__name__)


def fetch_thread_html(year, month):
    """Fetch thread.html from kernel-team mailing list archive for a given month."""
    url = f"https://lists.ubuntu.com/archives/kernel-team/{year}-{month}/thread.html"
    print(f"Fetching {url}...")
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def download_html(url):
    """Download HTML content from a URL."""
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        sys.exit(1)


def get_commits_from_html(html_content, sob_filter=None):
    """Extract and filter unlanded commits directly from OEM delta HTML content.

    Returns a list of dicts with keys: hash, subject, sob, public_bug,
    private_bugs, oem_project.
    """
    tabledata = extract_tabledata_from_html(html_content)
    print(f"  Found {len(tabledata)} total commits in HTML")

    # Only keep unlanded commits
    filtered = [
        c for c in tabledata
        if c.get('landed', '').strip().startswith('No')
    ]

    # Filter by Signed-off-by
    if sob_filter:
        filtered = [
            c for c in filtered
            if sob_filter.lower() in c.get('sob', '').lower()
        ]

    commits = [
        {
            'hash': c['hash'][:12],
            'subject': c['subject'],
            'sob': c.get('sob', ''),
            'public_bug': c.get('public_bug', ''),
            'private_bugs': c.get('private_bugs', ''),
            'oem_project': c.get('oem_project', ''),
        }
        for c in filtered
    ]

    print(f"  Found {len(commits)} commits after filtering (landed=No, sob={sob_filter})\n")
    return commits



_BRACKET_PREFIX_RE = re.compile(r'^(\[[^\]]*\]\s*)+')
_STATUS_PREFIX_RE = re.compile(
    r'^((?:ACK(?:ED)?|NACK|NAK|APPLIED|CMT|CMNT)'   # base keyword
    r'(?:[/](?:ACK(?:ED)?|NACK|NAK|APPLIED|CMT|CMNT))*'  # optional /combination
    r'(?:\[[^\]]*\])?)'                              # optional [qualifier] like [U][R][Q]
    r'\s*:?\s*(?:Re:)?\s*',
    re.IGNORECASE
)

def extract_status_prefix(subject):
    """Extract status prefix (ACK, NACK, NAK, CMNT, APPLIED, etc.) from email subject.
    Returns (prefix, subject_without_prefix). prefix is None if not present."""
    m = _STATUS_PREFIX_RE.match(subject)
    if m:
        prefix = m.group(1).upper().replace('ACKED', 'ACK')
        return prefix, subject[m.end():].strip()
    return None, subject


def normalize_subject(subject):
    """Strip status prefix, [SRU][R][PATCH x/y] style prefix and UBUNTU: SAUCE: prefix"""
    _, s = extract_status_prefix(subject)
    s = _BRACKET_PREFIX_RE.sub('', s).strip()
    s = s.replace('UBUNTU: SAUCE:', '').replace('UBUNTU:', '').strip()
    return s


_COVER_LETTER_RE = re.compile(r'\bPATCH(?:\s*v\d+)?\s+0+\s*/\s*\d+\b', re.IGNORECASE)
_PATCH_VERSION_RE = re.compile(r'(?:PATCH\s*v|(?<!\w)v)(\d+)\b', re.IGNORECASE)


def extract_patch_version(subject):
    """Extract patch version number from bracket tags in an email subject.
    Returns the version as an int (defaults to 1 if no version tag found).
    E.g. '[PATCH v3 2/5] fix foo' -> 3, '[PATCH 1/5] fix foo' -> 1
    """
    for bracket in re.findall(r'\[([^\]]*)\]', subject):
        m = _PATCH_VERSION_RE.search(bracket)
        if m:
            return int(m.group(1))
    return 1


def _status_priority(status):
    """Return numeric priority for status comparison. Higher = takes precedence.

    Priority (high to low): APPLIED(3) > NACK/NAK(2) > ACK/CMNT/other(1) > None(0)
    """
    if not status:
        return 0
    s = status.upper()
    if s.startswith('APPLIED'):
        return 3
    if s.startswith(('NACK', 'NAK')):
        return 2
    return 1


def _is_ack(prefix):
    """Return True if a status prefix represents an ACK (and not a NACK/NAK).

    Handles combined prefixes such as 'ACK/APPLIED' or 'ACK/CMNT'.
    """
    if not prefix:
        return False
    return any(token == 'ACK' for token in prefix.upper().split('/'))


def format_email_status(prefix, ack_count):
    """Format the status shown in the 'Emailed?' column.

    Appends the ACK tally as '<STATUS>*N' when the winning status is an ACK
    (including combined tags like 'ACK/CMNT') and the patch has 2+ ACKs, so the
    two-ACK 'ready to apply' threshold is visible at a glance. NACK/APPLIED/etc.
    outrank ACK (see _status_priority), so those are shown as-is with no tally.
    """
    if _is_ack(prefix) and ack_count and ack_count >= 2:
        return f"{prefix}*{ack_count}"
    return prefix


def parse_thread_html(html, base_url):
    """Parse thread.html into a flat list of entry dicts, tracking nesting depth.

    Each dict has: depth, subject, bare (subject without status prefix),
    link, prefix, inherited_prefix.
    Entries with 'The Daily Bug Report' in the subject are skipped.
    """
    entries = []
    depth = 0

    token_re = re.compile(
        r'<UL>|</UL>|<LI>\s*<A HREF="(\d+\.html)"[^>]*>(.*?)</A>',
        re.IGNORECASE | re.DOTALL
    )

    for m in token_re.finditer(html):
        tag = m.group(0)
        upper = tag.upper().lstrip()
        if upper.startswith('<UL'):
            depth += 1
        elif upper.startswith('</UL'):
            depth -= 1
        else:
            link_file = m.group(1)
            subject = unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip().replace('\n', ' ').strip()
            if not subject or 'The Daily Bug Report' in subject:
                continue
            prefix, bare = extract_status_prefix(subject)
            entries.append({
                'depth': depth,
                'subject': subject,
                'bare': bare if prefix else subject,
                'link': base_url + link_file,
                'prefix': prefix,
                'inherited_prefix': None,
                'inherited_ack_count': 0,
            })

    if entries:
        min_depth = min(e['depth'] for e in entries)
        for e in entries:
            e['depth'] -= min_depth

    return entries


def propagate_cover_letter_status(entries):
    """Propagate ACK/NACK from cover-letter reviews to sibling individual patches.

    For each thread (depth-0 root + descendants), if the root is a cover letter
    (PATCH 0/N) and a direct reply (depth 1) reviews that cover letter, propagate
    the review status to all other depth-1 children (the individual patches).

    Status priority (high to low): APPLIED > NACK > ACK = CMNT
    Higher-priority status always wins when multiple reviews exist.

    +-------------------------------------------------+------------------------------+
    | Situation                                       | Result                       |
    +-------------------------------------------------+------------------------------+
    | Cover letter ACK'd                              | All patches inherit ACK      |
    | Cover letter NACK'd                             | All patches inherit NACK     |
    | Cover letter ACK'd + one patch directly NACK'd  | Others ACK, that one NACK    |
    | Cover letter ACK'd + cover letter also NACK'd   | All patches NACK             |
    | Cover letter NACK'd + patch later APPLIED       | APPLIED wins (highest prio)  |
    +-------------------------------------------------+------------------------------+
    """
    i = 0
    while i < len(entries):
        if entries[i]['depth'] != 0:
            i += 1
            continue

        root = entries[i]
        root_norm = normalize_subject(root['bare']).lower()

        # Collect all entries in this thread (until next depth-0 entry)
        j = i + 1
        while j < len(entries) and entries[j]['depth'] > 0:
            j += 1

        thread = entries[i:j]
        direct_children = [e for e in thread if e['depth'] == 1]

        # Only propagate if root is a cover letter
        if _COVER_LETTER_RE.search(root['bare']):
            # Find the effective status from cover-letter reviews among direct children
            cover_status = None
            cover_ack_count = 0
            for child in direct_children:
                if not child['prefix']:
                    continue
                if normalize_subject(child['bare']).lower() == root_norm:
                    p = child['prefix']
                    if _is_ack(p):
                        cover_ack_count += 1
                    if _status_priority(p) > _status_priority(cover_status):
                        cover_status = p

            # Propagate to individual patch children (non-review depth-1 entries)
            if cover_status:
                for child in direct_children:
                    if child['prefix']:
                        continue
                    existing = child['inherited_prefix']
                    if _status_priority(cover_status) > _status_priority(existing):
                        child['inherited_prefix'] = cover_status
                    # Only add the cover's ACK tally to patches with a *different*
                    # normalized subject. In a single-patch series ([PATCH 0/1] +
                    # [PATCH 1/1]) the cover and patch share a subject, so the
                    # cover's ACKs are already counted under that subject by
                    # count_acks(); adding the inherited tally would double-count.
                    if (normalize_subject(child['bare']).lower() != root_norm
                            and cover_ack_count > child['inherited_ack_count']):
                        child['inherited_ack_count'] = cover_ack_count

        i = j


def count_acks(entries):
    """Count ACK reviews per (normalized subject, patch version).

    ACKs are tallied separately for each patch revision (v1, v2, ...) so that a
    respin never inherits the ACKs of an older version. Combines direct ACK
    replies (entries whose own status prefix is an ACK) with ACKs inherited from
    a cover letter (propagate_cover_letter_status stores that tally in each
    individual patch's 'inherited_ack_count').

    Returns: dict mapping (normalized_subject, version) -> ack_count (int).

    Note: counting is by ACK email, not by distinct reviewer. The thread index
    exposes only subjects, so a reviewer who ACKs both the cover letter and an
    individual patch may be counted twice for that patch.
    """
    direct = {}
    inherited = {}
    for entry in entries:
        norm = normalize_subject(entry['bare']).lower()
        if not norm:
            continue
        key = (norm, extract_patch_version(entry['subject']))
        if _is_ack(entry['prefix']):
            direct[key] = direct.get(key, 0) + 1
        ia = entry['inherited_ack_count']
        if ia > inherited.get(key, 0):
            inherited[key] = ia

    return {
        key: direct.get(key, 0) + inherited.get(key, 0)
        for key in set(direct) | set(inherited)
    }


def build_email_index(entries):
    """Build a subject index from parsed thread entries.

    Returns: dict mapping
        normalized_subject -> (original_subject, effective_prefix, version, link, ack_count)

    Only the LATEST patch version present for a subject is considered; once a
    respin exists (e.g. v2), every field reported here reflects that newest
    version and all older-version status/ACKs are ignored entirely. Among the
    latest-version entries, status priority APPLIED > NACK/NAK > ACK/CMNT/other
    decides the effective status; on a tie the first status-bearing entry wins so
    the link points at the patch submission rather than a later review reply.
    ack_count is the ACK tally for that latest version only (see count_acks).
    """
    ack_counts = count_acks(entries)

    groups = {}
    for entry in entries:
        norm = normalize_subject(entry['bare']).lower()
        if not norm:
            continue
        groups.setdefault(norm, []).append(entry)

    index = {}
    for norm, group in groups.items():
        latest_version = max(extract_patch_version(e['subject']) for e in group)

        best_subject = best_effective = best_link = None
        best_priority = -1
        for entry in group:
            if extract_patch_version(entry['subject']) != latest_version:
                continue
            effective = entry['prefix'] or entry['inherited_prefix']
            priority = _status_priority(effective)
            if priority > best_priority or (
                    priority == best_priority and not best_effective and effective):
                best_subject = entry['subject']
                best_effective = effective
                best_link = entry['link']
                best_priority = priority

        index[norm] = (
            best_subject,
            best_effective,
            latest_version,
            best_link,
            ack_counts.get((norm, latest_version), 0),
        )

    return index


def search_commit_in_archive(email_index, subject, year, month):
    """Search for a commit by comparing its subject against the pre-built email index.
    Returns (found, score, match_type, link, email_subject, email_prefix, version, ack_count)."""
    clean_subject = normalize_subject(subject).lower()
    subject_words = clean_subject.split()

    if not email_index:
        return False, 0, None, None, None, None, None, 0

    # Exact match on normalized subject
    if clean_subject in email_index:
        email_subj, prefix, version, link, ack_count = email_index[clean_subject]
        logger.debug(
            "[%s %s] EXACT match (100%%)\n"
            "  commit subject : %s\n"
            "  email subject  : %s\n"
            "  status prefix  : %s\n"
            "  version        : v%d\n"
            "  ack count      : %d",
            month, year, subject, email_subj, prefix or "none (original patch)", version, ack_count
        )
        return True, 100, "exact_subject", link, email_subj, prefix, version, ack_count

    # Fuzzy match: score by fraction of significant words found in normalized email subjects
    significant_words = [w for w in subject_words if len(w) > 3]
    if not significant_words:
        return False, 0, None, None, None, None, None, 0

    best_score = 0
    best_norm = None

    for norm_email in email_index:
        matches = sum(1 for w in significant_words if w in norm_email)
        score = int((matches / len(significant_words)) * 100)
        if score > best_score:
            best_score = score
            best_norm = norm_email

    if best_score >= 80:
        email_subj, prefix, version, link, ack_count = email_index[best_norm]
        logger.debug(
            "[%s %s] FUZZY match (%d%%)\n"
            "  commit subject : %s\n"
            "  email subject  : %s\n"
            "  status prefix  : %s\n"
            "  version        : v%d\n"
            "  ack count      : %d",
            month, year, best_score, subject, email_subj, prefix or "none (original patch)", version, ack_count
        )
        return True, best_score, "fuzzy_subject", link, email_subj, prefix, version, ack_count

    logger.debug(
        "[%s %s] NO match\n"
        "  commit subject : %s",
        month, year, subject
    )
    return False, 0, None, None, None, None, None, 0


def select_latest_match(matches):
    """Combine a commit's per-archive matches, keeping only the newest version.

    Threads can span multiple monthly archives, so a single patch version may be
    matched in more than one month. This keeps only the highest version number
    seen across all archives and, for that version, sums the ACK tallies from
    each archive and takes the highest-priority status
    (APPLIED > NACK/NAK > ACK/CMNT/other). Older versions are dropped entirely so
    a superseded revision never contributes its status or ACKs.

    matches: list of dicts with keys score, match_type, link, email_subject,
    email_prefix, version, ack_count.
    Returns a single combined dict, or None when matches is empty.
    """
    if not matches:
        return None

    latest_version = max(m['version'] for m in matches)
    latest = [m for m in matches if m['version'] == latest_version]

    # Representative record for the newest version: strongest status wins, with
    # match score as a tiebreaker so the clearest match supplies link/subject.
    rep = max(latest, key=lambda m: (_status_priority(m['email_prefix']), m['score']))

    return {
        'score': rep['score'],
        'match_type': rep['match_type'],
        'link': rep['link'],
        'email_subject': rep['email_subject'],
        'email_prefix': rep['email_prefix'],
        'version': latest_version,
        # ACK emails live in the month they were posted, so sum across archives
        # to get the full tally for this version (disjoint sets, no double count).
        'ack_count': sum(m['ack_count'] for m in latest),
    }


def print_thread_hierarchy(archives):
    """Print the email thread hierarchy for all fetched months."""
    for archive in archives:
        print(f"\n{'=' * 80}")
        print(f"Thread hierarchy: {archive['month']} {archive['year']}")
        print(f"{'=' * 80}")
        email_index = archive['email_index']
        for entry in archive['entries']:
            indent = '  ' * entry['depth']
            msg_id = entry['link'].rsplit('/', 1)[-1].replace('.html', '')
            # Review entries show their own direct prefix.
            # Original patch entries look up the index so that a higher-priority
            # direct review (e.g. NACK on the patch) overrides an inherited ACK
            # from the cover letter.
            norm = normalize_subject(entry['bare']).lower()
            info = email_index.get(norm, (None, None, None, None, 0))
            if entry['prefix']:
                status = entry['prefix']
            else:
                status = format_email_status(info[1], info[4])
            status_str = f"  [{status}]" if status else ''
            print(f"{indent}depth {entry['depth']}: {entry['subject']} ({msg_id}){status_str}")


def extract_tabledata_from_html(html_content):
    """Extract the JavaScript tabledata array from HTML"""
    match = re.search(r'var tabledata = \[(.*?)\];', html_content, re.DOTALL)
    if not match:
        raise ValueError("Could not find tabledata array in HTML")
    
    tabledata_str = '[' + match.group(1) + ']'
    
    # Fix JavaScript template literals (backticks) to regular strings
    def fix_template_literal(m):
        content = m.group(1)
        content = content.replace('\n', '').replace('\r', '').replace('\t', '')
        content = content.replace('"', '\\"')
        return '"' + content + '"'
    
    tabledata_str = re.sub(r'`([^`]*)`', fix_template_literal, tabledata_str)
    tabledata_str = re.sub(r',(\s*])', r'\1', tabledata_str)
    
    try:
        tabledata = json.loads(tabledata_str)
        return tabledata
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)


def generate_enhanced_html(original_html, results_dict):
    """Generate enhanced HTML with email information"""
    
    # Extract and update tabledata
    tabledata = extract_tabledata_from_html(original_html)
    
    # Add email info to tabledata
    for commit in tabledata:
        hash_val = commit['hash']
        
        # Match using first 12 chars since results use short hashes
        matched = False
        for result_hash, info in results_dict.items():
            if hash_val.startswith(result_hash):
                # This commit was checked and has results
                commit['emailed'] = (format_email_status(info['email_prefix'], info['ack_count']) if info['email_prefix'] else 'sent') if info['found'] else 'No'
                commit['email_match'] = f"{info['score']}%" if info['found'] else '-'
                commit['email_link'] = info['link'] if info['link'] else ''
                commit['email_archives'] = ', '.join(info['found_in']) if info['found_in'] else ''
                commit['email_version'] = f"v{info['version']}" if info['found'] and info['version'] is not None else '-'
                matched = True
                break
        
        if not matched:
            # Not checked (not matching filters), leave empty
            commit['emailed'] = ''
            commit['email_match'] = ''
            commit['email_link'] = ''
            commit['email_archives'] = ''
            commit['email_version'] = ''
    
    # Convert tabledata back to JavaScript
    tabledata_js = json.dumps(tabledata, indent=1)
    
    # Replace the tabledata in HTML
    new_html = re.sub(
        r'var tabledata = \[.*?\];',
        f'var tabledata = {tabledata_js};',
        original_html,
        flags=re.DOTALL
    )
    
    # Add new columns to the Tabulator columns definition
    columns_insert = '''			{title:"Emailed?", field:"emailed", sorter:"string", headerFilter:"input"},
			{title:"Version", field:"email_version", sorter:"string"},
			{title:"Email Match", field:"email_match", sorter:"string"},
			{title:"Email Link", field:"email_link", formatter:"link", sorter:"string", formatterParams: {target:"_blank"}},
			{title:"Found In", field:"email_archives", sorter:"string"},
'''
    
    # Insert before the "Signed-off-by" column
    new_html = re.sub(
        r'(\{title:"Signed-off-by")',
        columns_insert + r'\1',
        new_html
    )
    
    return new_html


def _md_cell(text):
    """Escape a value so it is safe inside a Markdown table cell."""
    if text is None:
        return ''
    text = str(text).replace('\r', ' ').replace('\n', ' ')
    return text.replace('|', '\\|')


def _format_public_bug(value):
    """Render the public_bug field as a Launchpad link (or '-')."""
    value = (value or '').strip()
    if not value:
        return '-'
    parts = []
    for bug in re.split(r'[,\s]+', value):
        bug = bug.strip()
        if not bug:
            continue
        if bug.isdigit():
            parts.append(f"[{bug}](https://bugs.launchpad.net/bugs/{bug})")
        else:
            parts.append(_md_cell(bug))
    return ', '.join(parts) if parts else '-'


def _format_private_bugs(value):
    """Render the private_bugs field (a stringified list) as Jira links (or '-')."""
    tickets = []
    if isinstance(value, (list, tuple)):
        tickets = list(value)
    elif value:
        try:
            import ast
            parsed = ast.literal_eval(value)
            tickets = parsed if isinstance(parsed, (list, tuple)) else [parsed]
        except (ValueError, SyntaxError):
            tickets = re.split(r'[,\s]+', str(value).strip('[]'))
    parts = []
    for ticket in tickets:
        ticket = str(ticket).strip().strip("'\"")
        if not ticket:
            continue
        parts.append(f"[{_md_cell(ticket)}](https://warthogs.atlassian.net/browse/{ticket})")
    return ', '.join(parts) if parts else '-'


def generate_markdown_report(results, source, months, found_count, not_found_count):
    """Build a GitHub-friendly Markdown report from the results list.

    Renders a native Markdown table (which GitHub displays as a real table),
    unlike the enhanced HTML whose rows live in a client-side JS array.
    """
    ready = [r for r in results
             if r['found'] and _is_ack(r['email_prefix']) and r['ack_count'] >= 2]

    lines = []
    lines.append(f"# Kernel-Team Email Check — {Path(urlparse(source).path).stem or source}")
    lines.append("")
    lines.append(f"_Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC_")
    lines.append("")
    lines.append(f"**Source:** {source}")
    lines.append("")
    lines.append(f"**Checked against:** last {months} month(s) of kernel-team archives")
    lines.append("")
    lines.append(
        f"**Summary:** {found_count} found, {not_found_count} not found · "
        f"{len(ready)} ready to apply (ACK'd with ≥2 ACKs)"
    )
    lines.append("")

    if ready:
        lines.append("## Ready to apply (≥2 ACKs)")
        lines.append("")
        for r in ready:
            lines.append(
                f"- `{_md_cell(r['hash'])}` "
                f"{_md_cell(format_email_status(r['email_prefix'], r['ack_count']))} — "
                f"{_md_cell(r['subject'])}"
            )
        lines.append("")

    lines.append("## All checked commits")
    lines.append("")
    lines.append("| Hash | Subject | Public bug | Private bug | Emailed? | Version | Match | Link | Found In | Signed-off-by |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in results:
        if r['found']:
            status = (format_email_status(r['email_prefix'], r['ack_count'])
                      if r['email_prefix'] else 'sent')
            version = f"v{r['version']}" if r['version'] is not None else '-'
            match = f"{r['score']}%"
            found_in = ', '.join(r['found_in']) if r['found_in'] else '-'
            link = f"[email]({r['link']})" if r.get('link') else '-'
        else:
            status, version, match, found_in, link = 'No', '-', '-', '-', '-'
        lines.append(
            f"| `{_md_cell(r['hash'])}` | {_md_cell(r['subject'])} | "
            f"{_format_public_bug(r.get('public_bug'))} | "
            f"{_format_private_bugs(r.get('private_bugs'))} | "
            f"{_md_cell(status)} | {version} | {match} | {link} | {_md_cell(found_in)} | "
            f"{_md_cell(r.get('sob', ''))} |"
        )
    lines.append("")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Check if unlanded commits have been sent to kernel-team mailing list',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text report: Check unlanded commits signed by Kuan-Ying
  %(prog)s https://kernel.ubuntu.com/oem-delta/oem-6.17-resolute.html --sob Kuan-Ying
  
  # HTML output: Create enhanced HTML with email info
  %(prog)s https://kernel.ubuntu.com/oem-delta/oem-6.17-resolute.html --sob Kuan-Ying --format html
  
  # Print thread hierarchy without needing an OEM delta file
  %(prog)s --print-hierarchy
  %(prog)s --print-hierarchy --months 1
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='URL or local HTML file from get-oem-delta.sh (not required with --print-hierarchy)'
    )
    
    parser.add_argument(
        '--months',
        type=int,
        default=3,
        help='Number of months to check (default: 3)'
    )
    
    parser.add_argument(
        '--sob',
        help='Filter by Signed-off-by name'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'html', 'markdown'],
        default='text',
        help='Output format: text report, enhanced HTML, or Markdown (default: text)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file name (for --format html or markdown). '
             'Defaults to <input>_enhanced.html or <input>.md'
    )

    parser.add_argument(
        '--html-output',
        help='Deprecated alias for --output (kept for backwards compatibility)'
    )


    parser.add_argument(
        '--print-hierarchy',
        action='store_true',
        help='Print the email thread hierarchy from the mailing list archives and exit'
    )

    parser.add_argument(
        '-d', '--debug',
        nargs='?',
        const='-',
        metavar='FILE',
        help='Enable debug output. Optionally write to FILE (default: stderr)'
    )

    args = parser.parse_args()

    if args.print_hierarchy and not args.input:
        # Allow running without input when only printing hierarchy
        pass
    elif not args.input:
        parser.error("input is required unless --print-hierarchy is used")

    if args.debug is not None:
        handler = (logging.FileHandler(args.debug)
                   if args.debug != '-'
                   else logging.StreamHandler())
        handler.setFormatter(logging.Formatter('[DEBUG] %(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine input type (URL or file)
    input_arg = args.input

    # Load HTML content once for reuse
    html_content = None
    if not args.print_hierarchy:
        if input_arg.startswith('http://') or input_arg.startswith('https://'):
            html_content = download_html(input_arg)
        else:
            html_file = Path(input_arg)
            if not html_file.exists():
                print(f"Error: File {html_file} not found")
                sys.exit(1)
            html_content = html_file.read_text()

        # Get commits to check
        print("=" * 80)
        print("STEP 1: Getting commits to check")
        print("=" * 80)
        commits = get_commits_from_html(html_content, sob_filter=args.sob)

        if not commits:
            print("No commits found to check")
            return

        print(f"Found {len(commits)} commits to check\n")
    
    # Fetch thread.html for the last N months
    print("=" * 80)
    print(f"STEP 2: Fetching last {args.months} months of thread indexes")
    print("=" * 80)

    now = datetime.now()
    archives = []

    for i in range(args.months):
        date = now - relativedelta(months=i)
        year = date.year
        month = date.strftime('%B')

        html = fetch_thread_html(year, month)
        if html:
            print(f"  Building email index for {month} {year}...")
            base_url = f"https://lists.ubuntu.com/archives/kernel-team/{year}-{month}/"
            entries = parse_thread_html(html, base_url)
            propagate_cover_letter_status(entries)
            archives.append({
                'year': year,
                'month': month,
                'entries': entries,
                'email_index': build_email_index(entries),
            })

    if not archives:
        print("\nNo thread indexes fetched successfully")
        return

    print(f"\nSuccessfully loaded {len(archives)} archives\n")

    if args.print_hierarchy:
        print_thread_hierarchy(archives)
        return
    
    # Search for each commit in the archives
    print("=" * 80)
    print("STEP 3: Checking commits in mailing list archives")
    print("=" * 80)
    print()
    
    results = []
    for commit in tqdm(commits, desc="Checking commits", unit="commit"):
        commit_hash = commit['hash']
        subject = commit['subject']
        
        found_in = []
        matches = []

        for archive in archives:
            found, score, match_type, link, email_subject, email_prefix, version, ack_count = search_commit_in_archive(
                archive['email_index'],
                subject,
                archive['year'],
                archive['month']
            )
            if found:
                found_in.append(f"{archive['month']} {archive['year']}")
                matches.append({
                    'score': score,
                    'match_type': match_type,
                    'link': link,
                    'email_subject': email_subject,
                    'email_prefix': email_prefix,
                    'version': version,
                    'ack_count': ack_count,
                })

        best = select_latest_match(matches) or {}

        results.append({
            'hash': commit_hash,
            'subject': subject,
            'sob': commit.get('sob', ''),
            'public_bug': commit.get('public_bug', ''),
            'private_bugs': commit.get('private_bugs', ''),
            'oem_project': commit.get('oem_project', ''),
            'found': len(found_in) > 0,
            'found_in': found_in,
            'score': best.get('score', 0),
            'match_type': best.get('match_type'),
            'link': best.get('link'),
            'email_subject': best.get('email_subject'),
            'email_prefix': best.get('email_prefix'),
            'version': best.get('version'),
            'ack_count': best.get('ack_count', 0),
        })
    
    # Print results
    print(f"{'Hash':<14} {'Status':<10} {'Ver':<5} {'Match':<6} {'In Archives':<35} {'Subject':<40}")
    print("-" * 115)
    
    found_count = 0
    not_found_count = 0
    
    for result in results:
        if result['found']:
            status = format_email_status(result['email_prefix'], result['ack_count']) if result['email_prefix'] else 'sent'
        else:
            status = "✗ NO"
        archives_str = ', '.join(result['found_in']) if result['found_in'] else '-'
        subject_short = result['subject'][:40]
        match_info = f"{result['score']}%" if result['found'] else "-"
        ver_str = f"v{result['version']}" if result['version'] is not None else "-"

        print(f"{result['hash']:<14} {status:<10} {ver_str:<5} {match_info:<6} {archives_str:<35} {subject_short:<40}")
        
        if result['found']:
            found_count += 1
        else:
            not_found_count += 1
    
    print("-" * 115)
    ready = [r for r in results if r['found'] and _is_ack(r['email_prefix']) and r['ack_count'] >= 2]
    print(f"\nSummary: {found_count} found, {not_found_count} not found in mailing list")
    print(f"         {len(ready)} ACK'd with >= 2 ACKs (ready to apply)")
    for r in ready:
        print(f"           - {r['hash']}  {format_email_status(r['email_prefix'], r['ack_count'])}  {r['subject'][:60]}")
    
    # Get filename from input (handle both URL and local path)
    if input_arg.startswith('http://') or input_arg.startswith('https://'):
        # Extract filename from URL
        parsed_url = urlparse(input_arg)
        input_filename = Path(parsed_url.path).stem
    else:
        input_filename = Path(input_arg).stem
    
    # Save detailed report only in debug mode
    if args.debug is not None:
        report_file = input_filename + '_email_check.txt'
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("KERNEL-TEAM MAILING LIST CHECK REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Checked against last {args.months} months of archives\n")
            f.write(f"Total commits checked: {len(commits)}\n")
            f.write(f"Found in mailing list: {found_count}\n")
            f.write(f"Not found in mailing list: {not_found_count}\n\n")
            
            f.write("COMMITS NOT FOUND IN MAILING LIST:\n")
            f.write("=" * 80 + "\n")
            for result in results:
                if not result['found']:
                    f.write(f"\nHash: {result['hash']}\n")
                    f.write(f"Subject: {result['subject']}\n")
            
            f.write("\n\nCOMMITS FOUND IN MAILING LIST:\n")
            f.write("=" * 80 + "\n")
            for result in results:
                if result['found']:
                    f.write(f"\nHash: {result['hash']}\n")
                    f.write(f"Subject: {result['subject']}\n")
                    f.write(f"Match: {result['score']}% ({result['match_type']})\n")
                    f.write(f"Status: {result['email_prefix'] if result['email_prefix'] else 'sent'}\n")
                    f.write(f"ACKs: {result['ack_count']}\n")
                    f.write(f"Version: v{result['version']}\n")
                    f.write(f"Found in: {', '.join(result['found_in'])}\n")
                    if result.get('link'):
                        f.write(f"Link: {result['link']}\n")
                    if result.get('email_subject'):
                        f.write(f"Matched email subject: {result['email_subject']}\n")
        
        print(f"\nDetailed report saved to: {report_file}")

    # Generate HTML output if requested
    if args.format == 'html':
        print("\n" + "=" * 80)
        print("STEP 4: Generating enhanced HTML")
        print("=" * 80)
        
        # Build results dictionary
        results_dict = {r['hash']: r for r in results}
        
        # Generate enhanced HTML (reuse html_content loaded in step 1)
        enhanced_html = generate_enhanced_html(html_content, results_dict)
        
        # Save HTML
        output_path = args.output or args.html_output
        if output_path:
            html_output = Path(output_path)
        else:
            html_output = Path(f"{input_filename}_enhanced.html")
        
        html_output.write_text(enhanced_html)
        print(f"\nEnhanced HTML saved to: {html_output}")
        print("New columns added: Emailed?, Version, Email Match, Email Link, Found In")

    # Generate Markdown output if requested
    if args.format == 'markdown':
        print("\n" + "=" * 80)
        print("STEP 4: Generating Markdown report")
        print("=" * 80)

        markdown = generate_markdown_report(
            results, input_arg, args.months, found_count, not_found_count
        )

        output_path = args.output or args.html_output
        if output_path:
            md_output = Path(output_path)
        else:
            md_output = Path(f"{input_filename}.md")

        md_output.write_text(markdown)
        print(f"\nMarkdown report saved to: {md_output}")


if __name__ == "__main__":
    main()
