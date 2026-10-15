# OpenAI Structured Output Contracts

All OpenAI calls must request strict JSON schema output.

## Job Recommendation

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "job_score",
    "interview_probability",
    "recommended_action",
    "resume_strategy",
    "best_project_to_highlight",
    "reasons",
    "missing_keywords"
  ],
  "properties": {
    "job_score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "interview_probability": { "type": "integer", "minimum": 0, "maximum": 100 },
    "recommended_action": { "type": "string" },
    "resume_strategy": { "type": "string" },
    "best_project_to_highlight": { "type": "string" },
    "reasons": { "type": "array", "items": { "type": "string" } },
    "missing_keywords": { "type": "array", "items": { "type": "string" } }
  }
}
```

## Recruiter Outreach

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["subject", "body", "requires_approval"],
  "properties": {
    "subject": { "type": "string" },
    "body": { "type": "string" },
    "requires_approval": { "type": "boolean", "const": true }
  }
}
```

## ATS Resume Score

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["ats_score", "missing_keywords", "project_emphasis", "improvements"],
  "properties": {
    "ats_score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "missing_keywords": { "type": "array", "items": { "type": "string" } },
    "project_emphasis": { "type": "array", "items": { "type": "string" } },
    "improvements": { "type": "array", "items": { "type": "string" } }
  }
}
```

