# Labeling guidelines

Labels describe only what the posting text states. When unsure, use null.

## Fields
- **company**: as named in the posting.
- **role_title**: only if it appears in the posting text; otherwise null.
- **location**: where *this job* is based, wherever in the posting it's stated (including
  "you can work hybrid from Toronto" in a nice-to-have list). City/province only.
  Use the job's own locations, not a list of the company's offices elsewhere in the
  posting (e.g. Clio: the job's "hub offices (Toronto, Calgary, Burnaby)", not the
  company-wide "Vancouver, Calgary, Toronto, Dublin and Sydney"). Multiple job locations
  are joined with "or".
- **work_mode**: remote, hybrid or onsite, only if explicitly stated. Don't infer it:
  "able to work from our Toronto office" does not say onsite → null.
  "Flexible working arrangements" alone is not a work mode → null.
- **term**: season, duration, or start/end dates. "Internship" or "co-op" alone → null.
- **deadline**: application deadline only, as written. Never a start or posting date.

## Skills
- **Resume test**: a skill must be something that would make sense in a resume's
  skills section. Named technologies (AWS, React, SQL) and specific concepts
  (object-oriented programming, CI/CD, version control) count.
- **These do not count:**
  - vague categories: "modern programming languages", "a Database Management System",
    "cloud platform", "IDE", "IT concepts"
  - activities: "data preparation", "data cleaning", "analysis", "software development
    and testing"
  - broad words on their own: "AI", "technology", "data", "automation"
  - experience requirements: "previous internship"
  - soft skills: communication, teamwork
- Every named technology is its own skill. If a platform and its services are
  named (AWS, S3, Lambda), list all of them.
- **Use the standard name** for a skill the posting describes in other words:
  "source control" → version control.
- **Fix obvious typos**: "JavaScripts" → JavaScript, "Microsoft Azures" → Microsoft Azure,
  "Phyton" → Python.
- **Required by default.** A skill is nice-to-have only if the posting marks it
  optional. Optional markers: "nice to have", "asset", "preferred", "bonus",
  "not required", and "What you may have" (it describes preferred, not required, skills).
  Headers like "What Makes You a Great Fit" are not optional markers → required.
- **Skills named in the job duties or a tech-stack list count**, and are required by
  default (e.g. "Support digital platforms including Atlassian, Planview, and Wrike" →
  Atlassian, Planview, Wrike). The tool's purpose is to show what to learn, and these
  are tools the team uses.
- **Conflicts:** if a skill appears in both a required and an optional place, a
  qualifications mention beats a nice-to-have mention, and a nice-to-have mention beats
  a duties/tech-stack mention. A skill never appears in both lists.

## Additional rules (adopted from the AI draft's decisions, reviewed by me)
- Examples count: "cloud platforms (e.g. AWS, Azure)" → AWS, Azure (not "cloud platforms").
- Concept plus tool: "version control (i.e. Git)" → both version control and Git.
- Compound service names are split: "ECS Fargate" → ECS, Fargate.
- Company-internal tools are excluded (they fail the resume test).
- role_title: a program or stream name counts when it's used as the position name.
- location: when a street address is given, use its city. Company HQ in boilerplate,
  a country only, or an unnamed province → null.
- work_mode: company-wide statements ("we are a hybrid organization") count. A choice
  offered to the candidate ("remote, hybrid, or onsite") → null.
- deadline: "Posting End Date" counts. "Open until filled" → null.
