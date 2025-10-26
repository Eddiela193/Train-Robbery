#!/usr/bin/env bash
# Educational script: explains SQL Injection basics and why it matters.
# Defensive/educational only — no exploit payloads or step-by-step attack instructions included.

echo -e "SQL Injection — conceptual walkthrough\n"
sleep 2

echo -e "What is SQL Injection?\n"
sleep 1
echo -e "SQL Injection (SQLi) is a class of vulnerability where untrusted input\nis interpreted by a database engine as part of an SQL command. When\napplications construct SQL statements by concatenating user input\nwithout appropriate safeguards, attackers can manipulate the resulting\nquery and cause the application to behave in unexpected ways.\n"
sleep 6

echo -e "Why does it happen?\n"
sleep 1
echo -e "At a high level, SQLi happens when three conditions occur together:\n\n  1) The application accepts input from an untrusted source (web form,\n     API parameter, cookie, etc.).\n  2) That input is embedded directly into SQL statements (e.g., via\n     string concatenation) instead of being bound as data.\n  3) The database server executes the resulting SQL statement without\n     separating code from data.\n\nThis mix-up — treating attacker-provided text as executable parts of\nSQL — is the root cause.\n"
sleep 8

echo -e "Simple (safe) illustration of a vulnerable pattern (pseudocode):\n"
sleep 1
cat <<'PSEUDO'
  // PSEUDOCODE — intentionally non-actionable
  // BAD: constructing SQL by concatenating raw user input
  user_input = get_input("user")
  query = "SELECT * FROM users WHERE username = '" + user_input + "';"
  db.execute(query)
PSEUDO
sleep 6

echo -e "Note: The pseudocode above is only to show the problematic pattern\n(string concatenation of input into SQL). Do NOT attempt to run or\nexploit anything. The correct approach is to separate query logic from\nuser data using parameterized statements (prepared statements) or\nORMs that bind data safely.\n"
sleep 6

echo -e "The string ' OR '5'='5 is particularly effective as 5=5 is always true\while not needed for the easier train, the quotation marks, when inserted
has the code the look like SELECT * FROM users WHERE username = '' OR '1'='1' AND password
 = 'anything';\nBe careful with 0s, or negative numbers, as programs may handle them differently 
than normal numbers\nTry an easy number in your exploits"
sleep 12

echo -e "What can go wrong? (high-level consequences)\n"
sleep 1
echo -e " - Data exposure: sensitive records returned that should be hidden.\n - Authentication bypass: attackers may influence login checks.\n - Data modification: attackers may insert, update, or delete data.\n - Denial of service: expensive queries may be triggered, exhausting\n   database resources.\n - Privilege escalation: combined with other flaws, attackers can\n   gain broader access or execute administrative commands.\n"
sleep 8

echo -e "Common categories of SQLi (conceptual)\n"
sleep 1
echo -e " - In-band SQLi: attacker sees results directly in the same channel\n   (easiest to detect).  \n - Blind SQLi: attacker must infer success via side effects (no direct\n   query results visible).  \n - Out-of-band techniques (rare): use alternative channels for results.\n\nAll are caused by the same root issue: untrusted data mixed with SQL\ncode.\n"
sleep 8

echo -e "How developers should prevent SQL Injection\n"
sleep 1
echo -e "1) Parameterized queries / prepared statements\n   - Use the database driver's parameter binding APIs; never build\n     dynamic SQL by concatenation.\n\n2) Use ORM or query builders when appropriate\n   - High-quality ORMs help separate code from data; still use bound\n     parameters for raw queries.\n\n3) Input validation and canonicalization\n   - Validate input format (length, type, allowed characters) for\n     business logic, but do not rely on validation alone for security.\n\n4) Least privilege for DB accounts\n   - Application DB user should have only the permissions it needs.\n     Avoid using admin/root DB accounts for the application.\n\n5) Escaping only as a last resort\n   - Proper escaping depends on context and DB engine; it is fragile\n     compared to parameterized queries.\n\n6) Use safe API functions for schema updates and migrations\n   - Avoid executing dynamically constructed DDL from untrusted data.\n"
sleep 12

echo -e "How to detect and monitor for SQLi (defensive signals)\n"
sleep 1
echo -e " - Unexpected or unusually large result sets returned by queries.\n - Application errors mentioning SQL or database internals in logs.\n - Repeated malformed requests hitting the same endpoint.\n - WAF alerts for suspicious payloads (tuned to avoid false positives).\n - Unusual spikes in DB query time or resource usage.\n"
sleep 8

echo -e "Safe testing & responsible practice\n"
sleep 1
echo -e " - Only test on systems you own, control, or have explicit written\n   permission to test (CTFs, lab VMs, staging environments).\n - Use automated scanners and fuzzers in controlled environments.\n - When fixing vulnerabilities, retest to ensure the fix works and\n   hasn't introduced other issues.\n - Keep business and security teams in the loop for disclosures and\n   remediation timelines.\n"
sleep 8

echo -e "High-level code example of safe usage (pseudocode):\n"
sleep 1
cat <<'SAFE'
  // PSEUDOCODE — defensive pattern
  user_input = get_input("user")
  // Use parameter binding instead of string concatenation:
  stmt = db.prepare("SELECT * FROM users WHERE username = ?")
  stmt.bind(1, user_input)
  results = stmt.execute()
SAFE
sleep 6

echo -e "Additional defensive tactics\n"
sleep 1
echo -e " - Use Web Application Firewalls (WAFs) as a compensating control,\n   but do not rely on them as the only protection.\n - Apply input and output encoding appropriate to the context (e.g.,\n   HTML encoding for web pages) to reduce impact from other classes of\n   injection.\n - Keep libraries and drivers up to date; many fixes are released for\n   DB drivers and frameworks.\n - Implement logging, rate limiting, and alerts to catch abuse early.\n"
sleep 8

echo -e "Resources & learning (defensive)\n"
sleep 1
echo -e " - OWASP SQL Injection Cheat Sheet — guidance for prevention and\n   examples of safe patterns.\n - OWASP Top Ten — explains injection and its place among common\n   web application risks.\n - Developer docs for your DB driver — look for prepared statement\n   examples in your language.\n\n(Visit canonical sources such as owasp.org and vendor docs for up-to-date\nsecurity guidance.)\n"
sleep 8

echo -e "Ethics and legality reminder\n"
sleep 1
echo -e "This material is for education and defense. Attempting SQL Injection\nagainst systems you do not own or for which you don't have explicit\npermission is illegal in many jurisdictions. Always follow lawful,\nethical practices — use labs, CTFs, or consented engagements for\npractical testing.\n"
sleep 4

echo -e "\nEnd of SQL Injection basics walkthrough. Stay curious and stay safe.\n"
