# Labeling guidelines

Labels describe only what the posting text states. When unsure, use null.

## Fields
- **company**: as named in the posting.
- **role_title**: only if it appears in the posting text; otherwise null.
- **location**: where the job is, wherever in the posting it's stated (including
  "you can work hybrid from Toronto" in a nice-to-have list). City/province only.
- **work_mode**: remote, hybrid or onsite, only if stated. "Flexible working
  arrangements" alone is not a work mode → null.
- **term**: season, duration, or start/end dates. "Internship" or "co-op" alone → null.
- **deadline**: application deadline only, as written. Never a start or posting date.

## Skills
- **Resume test**: a skill must be something that would make sense in a resume's
  skills section. Named technologies (AWS, React, SQL) and specific concepts
  (object-oriented programming, CI/CD, version control) count. Vague categories
  ("modern programming languages", "a Database Management System") do not.
- Every named technology is its own skill. If a platform and its services are
  named (AWS, S3, Lambda), list all of them.
- Soft skills (communication, teamwork) are never skills.
- **Required by default.** A skill is nice-to-have only if the posting explicitly
  marks it optional ("nice to have", "asset", "preferred", "bonus").