import type {
  CareerTargetingStrategy,
  DiscoveryResult,
  DraftResult,
  GithubProjectEvidence,
  InterviewPrepResult,
  Job,
  JobStatus,
  ResumeArtifact,
  ResumeCompilerStatus,
  SkillGapResult
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export const isApiConfigured = Boolean(API_BASE_URL);
export const apiBaseUrl = API_BASE_URL;

async function raiseApiError(response: Response, fallback: string): Promise<never> {
  let detail = fallback;
  try {
    const body = await response.json();
    detail = body.detail || body.message || detail;
  } catch {
    const text = await response.text();
    detail = text || detail;
  }
  throw new Error(`${detail} (${response.status})`);
}

export async function fetchJobs(accessToken?: string): Promise<Job[]> {
  if (!API_BASE_URL) {
    return [];
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to load jobs");
  }
  return response.json();
}

export async function createJob(
  payload: {
    title: string;
    company: string;
    location?: string;
    source?: string;
    url?: string;
    description: string;
  },
  accessToken?: string
): Promise<Job> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    body: JSON.stringify({
      source: "manual",
      location: "Australia",
      ...payload,
      url: payload.url || undefined
    })
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to save and score job");
  }
  return response.json();
}

export function absoluteApiUrl(path?: string): string | undefined {
  if (!path) {
    return undefined;
  }
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${API_BASE_URL}${path}`;
}

export async function discoverJobs(accessToken?: string, countries = "Australia"): Promise<DiscoveryResult> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const params = new URLSearchParams({ countries });
  const response = await fetch(`${API_BASE_URL}/api/jobs/discover?${params.toString()}`, {
    method: "POST",
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to discover live jobs");
  }
  return response.json();
}

export async function cleanupNonTargetJobs(accessToken?: string): Promise<{
  ignored: number;
  message: string;
}> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs/cleanup/non-target`, {
    method: "POST",
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to clean old non-target jobs");
  }
  return response.json();
}

export async function generateSkillGap(jobId: string, skills: string[], accessToken?: string): Promise<SkillGapResult> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/skill-gap`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    body: JSON.stringify({ skills })
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to generate skill gap");
  }
  return response.json();
}

export async function fetchProfileSkills(accessToken?: string): Promise<string[]> {
  if (!API_BASE_URL) {
    return [];
  }
  const response = await fetch(`${API_BASE_URL}/api/profile/skills`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to load saved skills");
  }
  const body = await response.json();
  return body.skills ?? [];
}

export async function saveProfileSkills(skills: string[], accessToken?: string): Promise<string[]> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/profile/skills`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    body: JSON.stringify({ skills })
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to save skills");
  }
  const body = await response.json();
  return body.skills ?? [];
}

export async function fetchGithubSkills(accessToken?: string): Promise<{
  skills: string[];
  projects: GithubProjectEvidence[];
  source: string;
}> {
  if (!API_BASE_URL) {
    return { skills: [], projects: [], source: "not_configured" };
  }
  const response = await fetch(`${API_BASE_URL}/api/profile/skills/github`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to read GitHub project skills");
  }
  return response.json();
}

export async function updateJobStatus(jobId: string, status: JobStatus, accessToken?: string): Promise<Job> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    body: JSON.stringify({ status })
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to update job status");
  }
  return response.json();
}

export async function generateResume(jobId: string, accessToken?: string): Promise<ResumeArtifact> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/resume`, {
    method: "POST",
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {}
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to generate resume");
  }
  return response.json();
}

export async function fetchResumeCompiler(accessToken?: string): Promise<ResumeCompilerStatus> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/resume/compiler`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to check PDF compiler");
  }
  return response.json();
}

export async function generateCoverNote(jobId: string, accessToken?: string): Promise<DraftResult> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/cover-note`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to generate cover note");
  }
  return response.json();
}

export async function generateOutreach(
  jobId: string,
  payload: {
    channel: "email" | "linkedin_connection" | "linkedin_dm";
    template_type: string;
    recipient_name?: string;
    recipient_role?: string;
    custom_context?: string;
  },
  accessToken?: string
): Promise<DraftResult> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/outreach`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to generate outreach draft");
  }
  return response.json();
}

export async function generateInterviewPrep(jobId: string, accessToken?: string): Promise<InterviewPrepResult> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/interview-prep`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to generate interview prep");
  }
  return response.json();
}

export async function sendDigest(period = "test", accessToken?: string): Promise<{
  subject: string;
  html: string;
  text: string;
}> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/digests`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    body: JSON.stringify({ period, send: true })
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to send digest");
  }
  return response.json();
}

export async function fetchCareerTargetingStrategy(accessToken?: string): Promise<CareerTargetingStrategy> {
  if (!API_BASE_URL) {
    throw new Error("Backend API URL is not configured");
  }
  const response = await fetch(`${API_BASE_URL}/api/career/targeting-strategy`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    cache: "no-store"
  });
  if (!response.ok) {
    await raiseApiError(response, "Unable to load career targeting strategy");
  }
  return response.json();
}
