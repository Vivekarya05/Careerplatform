"use client";

import {
  AlertTriangle,
  BarChart3,
  BriefcaseBusiness,
  CheckCircle2,
  Clock3,
  Copy,
  FileText,
  Gauge,
  Home,
  Info,
  Lightbulb,
  MessagesSquare,
  RefreshCw,
  Send,
  Settings,
  Target,
  Users,
  XCircle
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { JobCard } from "../components/JobCard";
import { MetricCard } from "../components/MetricCard";
import {
  createJob,
  discoverJobs,
  fetchGithubSkills,
  fetchJobs,
  fetchProfileSkills,
  fetchCareerTargetingStrategy,
  fetchResumeCompiler,
  absoluteApiUrl,
  generateCoverNote,
  generateInterviewPrep,
  generateOutreach,
  generateResume,
  generateSkillGap,
  isApiConfigured,
  saveProfileSkills,
  sendDigest,
  updateJobStatus
} from "../lib/api";
import { mockJobs, mockRecruiters } from "../lib/mock-data";
import { isAuthConfigured, isAuthRequired, supabase } from "../lib/supabase";
import type {
  CareerTargetingStrategy,
  DraftResult,
  GithubProjectEvidence,
  InterviewPrepResult,
  Job,
  JobStatus,
  ResumeArtifact,
  ResumeCompilerStatus,
  SkillGapResult
} from "../lib/types";

const tabs = [
  { label: "Dashboard", icon: Home },
  { label: "Live Jobs", icon: RefreshCw },
  { label: "Live Intake", icon: BriefcaseBusiness },
  { label: "Applications", icon: FileText },
  { label: "Recruiters", icon: Users },
  { label: "Skills", icon: Target },
  { label: "Resumes", icon: FileText },
  { label: "Interview Prep", icon: MessagesSquare },
  { label: "Insights", icon: BarChart3 },
  { label: "Settings", icon: Settings }
] as const;

type TabLabel = (typeof tabs)[number]["label"];

const SHORT_MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

type NoticeTone = "success" | "error" | "warning" | "info";

function classifyNotice(message: string): NoticeTone {
  const text = message.toLowerCase();
  if (text.includes("unable to") || text.includes("failed") || text.includes("not configured")) {
    return "error";
  }
  if (text.includes("sign in first") || text.includes("sign in to")) {
    return "warning";
  }
  if (
    text.includes("loaded") ||
    text.includes("saved") ||
    text.includes("scored") ||
    text.includes("generated") ||
    text.includes("sent:") ||
    text.includes("marked as") ||
    text.includes("analysed")
  ) {
    return "success";
  }
  return "info";
}

const NOTICE_ICONS: Record<NoticeTone, typeof CheckCircle2> = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertTriangle,
  info: Info
};

function sortedUnique(values: string[]) {
  return sortedUniqueRaw(values).sort((a, b) => a.localeCompare(b));
}

function sortedUniqueRaw(values: string[]) {
  return Array.from(new Set(values.map((value) => value.trim()).filter(Boolean)));
}

export default function HomePage() {
  const isDemoMode = !isApiConfigured;
  const [activeTab, setActiveTab] = useState<TabLabel>("Dashboard");
  const [email, setEmail] = useState("");
  const [jobs, setJobs] = useState<Job[]>(isDemoMode ? mockJobs : []);
  const [isSignedIn, setIsSignedIn] = useState(!isAuthRequired || !isAuthConfigured);
  const [draft, setDraft] = useState<DraftResult | null>(null);
  const [draftCopied, setDraftCopied] = useState(false);
  const [skillGap, setSkillGap] = useState<SkillGapResult | null>(null);
  const [interviewPrep, setInterviewPrep] = useState<InterviewPrepResult | null>(null);
  const [interviewJob, setInterviewJob] = useState<Job | null>(null);
  const [careerStrategy, setCareerStrategy] = useState<CareerTargetingStrategy | null>(null);
  const [compiler, setCompiler] = useState<ResumeCompilerStatus | null>(null);
  const [githubSkillProjects, setGithubSkillProjects] = useState<GithubProjectEvidence[]>([]);
  const [isLoadingGithubSkills, setIsLoadingGithubSkills] = useState(false);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [isSendingDigest, setIsSendingDigest] = useState(false);
  const [isLoadingStrategy, setIsLoadingStrategy] = useState(false);
  const [busyJobId, setBusyJobId] = useState<string | null>(null);
  const [resumeArtifacts, setResumeArtifacts] = useState<ResumeArtifact[]>([]);
  const [countryFilter, setCountryFilter] = useState("Australia");
  const [selectedMonthKey, setSelectedMonthKey] = useState("");
  const [skillText, setSkillText] = useState(
    "Business Analysis, Requirements Gathering, Stakeholder Management, Process Improvement, Utilities Transformation, Market Systems, Trading Systems, Energy Software, Metering, DER, Asset Management, Python, SQL, PostgreSQL, Power BI, DAX, Pandas, NumPy, XGBoost, TensorFlow, Keras, AEMO NEM Data, Dispatch Pricing, FCAS, Demand Analysis, Renewable Integration, Battery Storage Analytics, PLEXOS Cloud, Forecasting, Trading Analytics"
  );
  const [jobForm, setJobForm] = useState({
    title: "",
    company: "",
    location: "Australia",
    url: "",
    description: ""
  });
  const [notice, setNotice] = useState(
    isDemoMode
      ? "Demo mode: connect the backend API URL for live data."
      : isAuthRequired
        ? "Sign in to load your private job data."
        : "Live public mode enabled. Discover jobs or add a job description."
  );

  useEffect(() => {
    if (!isAuthRequired) {
      fetchJobs()
        .then((liveJobs) => {
          setJobs(liveJobs);
          setNotice(
            liveJobs.length > 0
              ? "Live job intelligence loaded."
              : "Live public mode enabled. Click Discover jobs to pull fresh opportunities."
          );
        })
        .catch(() => {
          setJobs([]);
          setNotice("Live backend request failed. Check Render deploy and NEXT_PUBLIC_API_BASE_URL.");
        });
      return;
    }
    if (!supabase) {
      return;
    }
    supabase.auth.getSession().then(({ data }) => {
      const token = data.session?.access_token;
      setIsSignedIn(Boolean(token));
      if (!token) {
        return;
      }
      fetchJobs(token)
        .then((liveJobs) => {
          if (liveJobs.length > 0) {
            setJobs(liveJobs);
            setNotice("Live job intelligence loaded.");
          } else {
            setJobs([]);
            setNotice("Signed in. Add a job description to score your first live opportunity.");
          }
        })
        .catch(() => {
          setJobs([]);
          setNotice("Signed in, but the live backend request failed. Check Render deploy and NEXT_PUBLIC_API_BASE_URL.");
        });
    });
  }, []);

  const countryKeywords: Record<string, string[]> = {
    Australia: ["australia", "sydney", "melbourne", "brisbane", "perth", "adelaide", "canberra", "nsw", "vic", "qld", "wa", "sa", "act", "tas", "nt"]
  };
  const filteredJobs = useMemo(() => {
    const selected = countryFilter.split(",").map((item) => item.trim()).filter(Boolean);
    const keywords = selected.flatMap((country) => countryKeywords[country] ?? [country.toLowerCase()]);
    if (keywords.length === 0) {
      return jobs;
    }
    return jobs.filter((job) => keywords.some((keyword) => (job.location ?? "").toLowerCase().includes(keyword)));
  }, [jobs, countryFilter]);
  const topJobs = useMemo(() => [...filteredJobs].sort((a, b) => b.score - a.score), [filteredJobs]);
  const avgScore = Math.round(filteredJobs.reduce((sum, job) => sum + job.score, 0) / Math.max(filteredJobs.length, 1));
  const topJob = topJobs[0];
  const noticeTone = useMemo(() => classifyNotice(notice), [notice]);
  const NoticeIcon = NOTICE_ICONS[noticeTone];
  const monthlyRoleReleases = useMemo(() => {
    const monthKeys = Array.from({ length: 6 }, (_, index) => {
      const date = new Date();
      date.setDate(1);
      date.setMonth(date.getMonth() - (5 - index));
      return {
        key: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`,
        label: SHORT_MONTH_NAMES[date.getMonth()],
        total: 0,
        families: {
          "Energy market": 0,
          BESS: 0,
          Forecasting: 0,
          Trading: 0,
          "Data/BI": 0,
          Renewables: 0
        } as Record<string, number>
      };
    });
    const monthMap = new Map(monthKeys.map((month) => [month.key, month]));

    function familyFor(job: Job) {
      const text = `${job.title} ${job.description ?? ""} ${job.score_breakdown.best_project_to_highlight ?? ""}`.toLowerCase();
      if (text.includes("bess") || text.includes("battery") || text.includes("storage")) return "BESS";
      if (text.includes("forecast") || text.includes("demand")) return "Forecasting";
      if (text.includes("trading") || text.includes("dispatch") || text.includes("spot price")) return "Trading";
      if (text.includes("power bi") || text.includes("data") || text.includes("sql") || text.includes("python")) return "Data/BI";
      if (text.includes("renewable") || text.includes("solar") || text.includes("wind")) return "Renewables";
      return "Energy market";
    }

    filteredJobs.forEach((job) => {
      const rawDate = job.posted_at ?? job.created_at ?? job.updated_at;
      const date = rawDate ? new Date(rawDate) : new Date();
      if (Number.isNaN(date.getTime())) {
        return;
      }
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
      const month = monthMap.get(key);
      if (!month) {
        return;
      }
      month.total += 1;
      month.families[familyFor(job)] += 1;
    });
    return monthKeys;
  }, [filteredJobs]);
  const maxMonthlyReleases = Math.max(1, ...monthlyRoleReleases.map((month) => month.total));
  const selectedMonth = monthlyRoleReleases.find((month) => month.key === selectedMonthKey) ?? monthlyRoleReleases[monthlyRoleReleases.length - 1];
  const selectedMonthJobs = useMemo(() => {
    if (!selectedMonth) {
      return [];
    }
    return topJobs.filter((job) => {
      const rawDate = job.posted_at ?? job.created_at ?? job.updated_at;
      const date = rawDate ? new Date(rawDate) : new Date();
      if (Number.isNaN(date.getTime())) {
        return false;
      }
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}` === selectedMonth.key;
    });
  }, [selectedMonth, topJobs]);
  const canUseLiveApp = isDemoMode || isSignedIn;
  const visibleJobs = activeTab === "Dashboard" ? topJobs.filter((job) => job.status !== "ignored").slice(0, 8) : topJobs;
  const profileSkills = useMemo(
    () => skillText.split(/[,;\n]/).map((skill) => skill.trim()).filter(Boolean),
    [skillText]
  );

  useEffect(() => {
    const savedSkills = window.localStorage.getItem("career-os-skills");
    if (savedSkills) {
      setSkillText(savedSkills);
    }
  }, []);

  useEffect(() => {
    if (!canUseLiveApp) {
      return;
    }
    async function loadSkills() {
      try {
        const token = await getToken();
        const saved = await fetchProfileSkills(token);
        if (saved.length > 0) {
          setSkillText(saved.join(", "));
          window.localStorage.setItem("career-os-skills", saved.join(", "));
        }
      } catch {
        // Keep local skills if the live profile is not available yet.
      }
    }
    void loadSkills();
  }, [canUseLiveApp]);

  useEffect(() => {
    if (!canUseLiveApp) {
      return;
    }
    async function loadCompiler() {
      try {
        const token = await getToken();
        setCompiler(await fetchResumeCompiler(token));
      } catch {
        setCompiler(null);
      }
    }
    void loadCompiler();
  }, [canUseLiveApp]);

  function getToken() {
    return supabase?.auth.getSession().then(({ data }) => data.session?.access_token);
  }

  async function selectTab(tab: TabLabel) {
    setActiveTab(tab);
    if (tab === "Live Jobs" && canUseLiveApp && jobs.length === 0 && !isDiscovering) {
      await handleDiscoverJobs();
    }
  }

  async function sendMagicLink() {
    if (!supabase || !email) {
      return;
    }
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: window.location.origin }
    });
    setNotice(error ? error.message : "Check your email for the sign-in link.");
  }

  async function handleGenerateResume(job: Job) {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then generate the tailored resume PDF.");
      return;
    }
    setBusyJobId(job.id);
    try {
      const artifact = await generateResume(job.id, token);
      setResumeArtifacts((current) => [artifact, ...current]);
      setNotice(
        artifact.pdf_generated
          ? `Resume saved: ${artifact.pdf_filename}`
          : `Resume LaTeX saved as ${artifact.pdf_filename.replace(".pdf", ".tex")}; PDF needs latexmk in backend.`
      );
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to generate resume yet.");
    } finally {
      setBusyJobId(null);
    }
  }

  async function handleGenerateCover(job: Job) {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then generate the cover note.");
      return;
    }
    setBusyJobId(job.id);
    try {
      const generated = await generateCoverNote(job.id, token);
      setDraft({ ...generated, channel: "cover letter" });
      setNotice("Cover note generated. Review before sending.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to generate cover note yet.");
    } finally {
      setBusyJobId(null);
    }
  }

  async function handleGenerateOutreach(job: Job) {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then generate outreach drafts.");
      return;
    }
    setBusyJobId(job.id);
    try {
      const generated = await generateOutreach(
        job.id,
        {
          channel: "email",
          template_type: "cold_outreach",
          custom_context: "Please keep this professional, short, and Australian energy-market focused."
        },
        token
      );
      setDraft(generated);
      setNotice("Outreach draft generated. Review before sending.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to generate outreach draft yet.");
    } finally {
      setBusyJobId(null);
    }
  }

  async function handleCreateJob(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then add and score live jobs.");
      return;
    }
    try {
      const created = await createJob(jobForm, token);
      setJobs((current) => [created, ...current.filter((job) => job.id !== created.id)]);
      setNotice(`${created.company} scored ${created.score}/100 and was saved.`);
      setJobForm({ title: "", company: "", location: "Australia", url: "", description: "" });
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to save job yet.");
    }
  }

  async function handleDiscoverJobs() {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then discover live jobs.");
      return;
    }
    setIsDiscovering(true);
    setNotice("Discovering live Energy/NEM/BESS jobs now...");
    try {
      const result = await discoverJobs(token, countryFilter);
      setJobs(result.jobs);
      setNotice(result.message);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to discover live jobs right now.");
    } finally {
      setIsDiscovering(false);
    }
  }

  async function handleSendTestDigest() {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then send a test digest.");
      return;
    }
    setIsSendingDigest(true);
    try {
      const preview = await sendDigest("test", token);
      setNotice(`Test digest sent: ${preview.subject}`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to send test digest.");
    } finally {
      setIsSendingDigest(false);
    }
  }

  async function handleLoadCareerStrategy() {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then generate the career strategy.");
      return;
    }
    setIsLoadingStrategy(true);
    try {
      const strategy = await fetchCareerTargetingStrategy(token);
      setCareerStrategy(strategy);
      setActiveTab("Insights");
      setNotice(`Career strategy loaded from ${strategy.source}.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to load career strategy.");
    } finally {
      setIsLoadingStrategy(false);
    }
  }

  async function handleUpdateStatus(job: Job, status: JobStatus) {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then update applications.");
      return;
    }
    setBusyJobId(job.id);
    try {
      const updated = await updateJobStatus(job.id, status, token);
      setJobs((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setNotice(`${updated.company} marked as ${status}.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to update job status.");
    } finally {
      setBusyJobId(null);
    }
  }

  async function handleApply(job: Job) {
    if (job.url) {
      window.open(job.url, "_blank", "noopener,noreferrer");
    }
    await handleUpdateStatus(job, "applied");
  }

  async function handleGenerateSkillGap(job: Job) {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then analyse skill gaps.");
      return;
    }
    setBusyJobId(job.id);
    try {
      const generated = await generateSkillGap(job.id, profileSkills, token);
      setSkillGap(generated);
      setActiveTab("Skills");
      setNotice(`Skill gap analysed for ${job.title}.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to generate skill gap.");
    } finally {
      setBusyJobId(null);
    }
  }

  async function handleGenerateInterviewPrep(job: Job) {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then generate interview prep.");
      return;
    }
    setBusyJobId(job.id);
    try {
      const generated = await generateInterviewPrep(job.id, token);
      const updated = await updateJobStatus(job.id, "interviewing", token);
      setJobs((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setInterviewPrep(generated);
      setInterviewJob(updated);
      setActiveTab("Interview Prep");
      setNotice(`Interview prep generated for ${job.company}. Focus on ${generated.recommended_project.name}.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to generate interview prep.");
    } finally {
      setBusyJobId(null);
    }
  }

  async function saveSkills() {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then save skills to your profile.");
      return;
    }
    const skills = skillText.split(/[,;\n]/).map((skill) => skill.trim()).filter(Boolean);
    window.localStorage.setItem("career-os-skills", skills.join(", "));
    try {
      const saved = await saveProfileSkills(skills, token);
      setSkillText(saved.join(", "));
      setNotice("Skill profile saved. Future skill-gap checks and resume strategy will use it.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Saved locally, but live skill save failed.");
    }
  }

  async function loadGithubSkills() {
    const token = await getToken();
    if (isAuthRequired && !token) {
      setNotice("Sign in first, then read GitHub project skills.");
      return;
    }
    setIsLoadingGithubSkills(true);
    try {
      const result = await fetchGithubSkills(token);
      setGithubSkillProjects(result.projects);
      if (result.skills.length > 0) {
        const merged = sortedUnique([...profileSkills, ...result.skills]);
        setSkillText(merged.join(", "));
        window.localStorage.setItem("career-os-skills", merged.join(", "));
        await saveProfileSkills(merged, token);
        setNotice(`Imported ${result.skills.length} skills from GitHub README evidence.`);
      } else {
        setNotice("No GitHub README skills found yet. Add clear README keywords to your project repos.");
      }
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to read GitHub project skills.");
    } finally {
      setIsLoadingGithubSkills(false);
    }
  }

  function openDownload(path?: string) {
    const url = absoluteApiUrl(path);
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  }

  async function handleCopyDraft() {
    if (!draft) {
      return;
    }
    try {
      await navigator.clipboard.writeText(draft.body);
      setDraftCopied(true);
      setTimeout(() => setDraftCopied(false), 2000);
    } catch {
      setNotice("Unable to copy draft. Select the text and copy manually.");
    }
  }

  const renderJobCard = (job: Job) => (
    <JobCard
      isBusy={busyJobId === job.id}
      job={job}
      key={job.id}
      onApply={handleApply}
      onGenerateCover={handleGenerateCover}
      onGenerateOutreach={handleGenerateOutreach}
      onGenerateResume={handleGenerateResume}
      onGenerateSkillGap={handleGenerateSkillGap}
      onGenerateInterviewPrep={handleGenerateInterviewPrep}
      onUpdateStatus={handleUpdateStatus}
    />
  );

  return (
    <main className="shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand">
          <Gauge size={24} />
          <div>
            <strong>Career OS</strong>
            <span>Energy Market Analytics</span>
          </div>
        </div>
        <nav>
          {tabs.map((tab, index) => {
            const Icon = tab.icon;
            return (
              <button
                className={activeTab === tab.label ? "active" : ""}
                key={tab.label}
                onClick={() => void selectTab(tab.label)}
                type="button"
              >
                <Icon size={18} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Sydney, Australia</p>
            <h1>Vivek's Energy Career Intelligence</h1>
            <p className={`topbar__notice topbar__notice--${noticeTone}`}>
              <NoticeIcon size={16} />
              <span>{notice}</span>
            </p>
          </div>
          <button className="primary-action">
            <Lightbulb size={18} />
            What should I do today?
          </button>
        </header>

        {isAuthRequired && isAuthConfigured && !isSignedIn ? (
          <section className="auth-panel">
            <div>
              <p className="eyebrow">Private access</p>
              <h2>Sign in to your career OS</h2>
            </div>
            <div className="auth-row">
              <input
                aria-label="Email address"
                onChange={(event) => setEmail(event.target.value)}
                placeholder="vivek@example.com"
                type="email"
                value={email}
              />
              <button onClick={sendMagicLink}>Send link</button>
            </div>
          </section>
        ) : null}

        <section className="command-panel" aria-label="Daily job intelligence controls">
          <div>
            <p className="eyebrow">Daily command centre</p>
            <h2>Live job discovery</h2>
            <p>Fetches Australian energy and utilities roles across business analysis, market systems, trading systems, DER, BESS, metering, operations, commercial analytics and forecasting. LinkedIn stays manual: paste links or descriptions into intake.</p>
          </div>
          <div className="command-actions">
            <label>
              Market
              <select
                aria-label="Australian market filter"
                onChange={(event) => setCountryFilter(event.target.value)}
                value={countryFilter}
              >
                <option value="Australia">Australia only</option>
              </select>
            </label>
            <button className="primary-action" disabled={isDiscovering || !canUseLiveApp} onClick={handleDiscoverJobs}>
              <RefreshCw size={18} />
              {isDiscovering ? "Fetching..." : "Fetch jobs"}
            </button>
            <button disabled={isSendingDigest || !canUseLiveApp} onClick={handleSendTestDigest}>
              <Send size={18} />
              {isSendingDigest ? "Sending..." : "Send test digest"}
            </button>
            <button disabled={isLoadingStrategy || !canUseLiveApp} onClick={handleLoadCareerStrategy}>
              <Lightbulb size={18} />
              {isLoadingStrategy ? "Thinking..." : "AI strategy"}
            </button>
          </div>
        </section>

        <section className="metrics-grid" aria-label="Career metrics">
          <MetricCard
            label="Top opportunity"
            value={topJob ? `${topJob.score}/100` : "--"}
            detail={topJob ? `${topJob.company} fit score` : "Add a live job first"}
          />
          <MetricCard label="Average fit" value={topJobs.length ? `${avgScore}/100` : "--"} detail="Across active jobs" />
          <MetricCard label="Recruiter actions" value={jobs.filter((job) => job.status === "saved").length.toString()} detail="Saved jobs to follow up" />
          <MetricCard label="Interview ratio" value="0%" detail="Starts after first applications" />
        </section>

        {activeTab === "Live Intake" && canUseLiveApp ? (
          <section className="panel intake-panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Live intake</p>
                <h2>Add a job to score</h2>
              </div>
            </div>
            <form className="job-form" onSubmit={handleCreateJob}>
              <input
                aria-label="Job title"
                onChange={(event) => setJobForm((current) => ({ ...current, title: event.target.value }))}
                placeholder="Job title"
                required
                value={jobForm.title}
              />
              <input
                aria-label="Company"
                onChange={(event) => setJobForm((current) => ({ ...current, company: event.target.value }))}
                placeholder="Company"
                required
                value={jobForm.company}
              />
              <input
                aria-label="Location"
                onChange={(event) => setJobForm((current) => ({ ...current, location: event.target.value }))}
                placeholder="Location"
                value={jobForm.location}
              />
              <input
                aria-label="Job URL"
                onChange={(event) => setJobForm((current) => ({ ...current, url: event.target.value }))}
                placeholder="Job link"
                type="url"
                value={jobForm.url}
              />
              <textarea
                aria-label="Job description"
                onChange={(event) => setJobForm((current) => ({ ...current, description: event.target.value }))}
                placeholder="Paste job description here. The platform will score Business Analyst in Energy, utilities, market systems, trading systems, DER, BESS, NEM, forecasting, SQL/Python, and Power BI fit."
                required
                value={jobForm.description}
              />
              <button className="primary-action" type="submit">Save and score job</button>
            </form>
          </section>
        ) : !canUseLiveApp ? (
          <section className="locked-panel">
            <h2>Private dashboard locked</h2>
            <p>Sign in with your email to add live jobs, score opportunities, generate resumes, and create outreach drafts.</p>
          </section>
        ) : null}

        {activeTab === "Live Jobs" ? (
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Live jobs</p>
                <h2>All scored live opportunities</h2>
              </div>
              <div className="inline-controls">
                <select
                  aria-label="Country filter"
                  onChange={(event) => setCountryFilter(event.target.value)}
                  value={countryFilter}
                >
                  <option value="Australia">Australia only</option>
                </select>
                <button disabled={isDiscovering || !canUseLiveApp} onClick={handleDiscoverJobs}>
                  {isDiscovering ? "Discovering..." : "Discover jobs"}
                </button>
              </div>
            </div>
            <div className="job-list">
              {topJobs.length === 0 ? (
                <div className="empty-state">
                  <h3>No live jobs yet</h3>
                  <p>No Australian jobs are currently visible. Click Discover jobs, or paste a matching Australian job from Seek, company careers, or a manual LinkedIn link.</p>
                </div>
              ) : null}
              {topJobs.map(renderJobCard)}
            </div>
          </section>
        ) : null}

        {activeTab === "Applications" ? (
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Pipeline</p>
                <h2>Applications</h2>
              </div>
            </div>
            <div className="status-grid">
              {["saved", "applied", "interviewing", "closed"].map((status) => (
                <div className="status-column" key={status}>
                  <h3>{status}</h3>
                  <strong>{jobs.filter((job) => job.status === status).length}</strong>
                </div>
              ))}
            </div>
            <div className="job-list tab-list">
              {topJobs.filter((job) => job.status !== "ignored").map(renderJobCard)}
            </div>
          </section>
        ) : null}

        {activeTab === "Recruiters" ? (
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">CRM</p>
                <h2>Recruiter follow-ups</h2>
              </div>
              <button onClick={() => setNotice("Recruiter CRM write actions are the next build step.")}>Reach out</button>
            </div>
            <div className="recruiter-list">
              {(isDemoMode ? mockRecruiters : []).map((recruiter) => (
                <article className="recruiter-row" key={recruiter.id}>
                  <div>
                    <strong>{recruiter.name}</strong>
                    <span>{recruiter.company}</span>
                    <small>{recruiter.focus_area}</small>
                  </div>
                  <div className="quality">{recruiter.quality_score}</div>
                </article>
              ))}
              {!isDemoMode ? (
                <div className="empty-state">
                  <h3>No live recruiters yet</h3>
                  <p>Use Reach Out on a job to draft recruiter messages. Full CRM records come next.</p>
                </div>
              ) : null}
            </div>
          </section>
        ) : null}

        {activeTab === "Skills" ? (
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Skill profile</p>
                <h2>Your evolving skills</h2>
              </div>
              <div className="inline-controls">
                <button disabled={isLoadingGithubSkills} onClick={() => void loadGithubSkills()}>
                  {isLoadingGithubSkills ? "Reading GitHub..." : "Import GitHub skills"}
                </button>
                <button onClick={() => void saveSkills()}>Save skills</button>
              </div>
            </div>
            <textarea
              aria-label="Skills"
              onChange={(event) => setSkillText(event.target.value)}
              value={skillText}
            />
            {skillGap ? (
              <div className="insight-block">
                <h3>Latest skill gap</h3>
                <p>{skillGap.positioning}</p>
                <strong>Matched</strong>
                <div className="keyword-row">
                  {skillGap.matched_skills.map((skill) => <span key={skill}>{skill}</span>)}
                </div>
                <strong>Missing or weak evidence</strong>
                <div className="keyword-row">
                  {skillGap.missing_skills.map((skill) => <span key={skill}>{skill}</span>)}
                </div>
                <ul className="brief-list">
                  {skillGap.recommended_learning.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>
            ) : (
              <div className="empty-state">
                <h3>No skill gap selected</h3>
                <p>Click Skill Gap on any job card. This uses the skills above, not only your resume.</p>
              </div>
            )}
            {githubSkillProjects.length > 0 ? (
              <div className="insight-block">
                <h3>GitHub project evidence</h3>
                <div className="project-evidence-list">
                  {githubSkillProjects.map((project) => (
                    <article className="project-evidence" key={project.repo}>
                      <a href={project.url} rel="noreferrer" target="_blank">{project.repo}</a>
                      <p>{project.summary}</p>
                      <div className="keyword-row">
                        {project.skills.slice(0, 8).map((skill) => <span key={`${project.repo}-${skill}`}>{skill}</span>)}
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            ) : null}
          </section>
        ) : null}

        {activeTab === "Resumes" ? (
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Resume engine</p>
                <h2>Tailored resumes</h2>
              </div>
              <span className={compiler?.available ? "health-pill good" : "health-pill warn"}>
                PDF compiler: {compiler?.available ? "Ready" : "Unavailable"}
              </span>
            </div>
            {compiler ? (
              <div className="compiler-strip">
                <strong>{compiler.pdf_compiler}</strong>
                <span>{compiler.message}</span>
              </div>
            ) : null}
            {resumeArtifacts.length > 0 ? (
              <div className="artifact-list">
                {resumeArtifacts.map((artifact) => (
                  <article className="artifact-row" key={`${artifact.pdf_filename}-${artifact.storage_path ?? "local"}`}>
                    <strong>{artifact.pdf_filename}</strong>
                    <span>{artifact.pdf_generated ? "PDF generated" : "LaTeX saved; PDF compiler unavailable"}</span>
                    <button onClick={() => openDownload(artifact.download_url)}>Download</button>
                  </article>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <h3>Generate from a job card</h3>
                <p>Open Dashboard or Live Jobs, then click Resume on any scored job. Each version uses your premium LaTeX format and company-role filename.</p>
              </div>
            )}
            <div className="job-list tab-list">{topJobs.slice(0, 6).map(renderJobCard)}</div>
          </section>
        ) : null}

        {activeTab === "Interview Prep" ? (
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Preparation</p>
                <h2>{interviewJob ? `${interviewJob.company} interview engine` : "Interview Prep"}</h2>
              </div>
            </div>
            {interviewPrep ? (
              <div className="interview-workbench">
                <article className="prep-hero">
                  <p className="eyebrow">Company briefing</p>
                  <h3>{interviewJob?.title}</h3>
                  <p>{interviewPrep.company_briefing}</p>
                </article>
                <article className="insight-block">
                  <p className="eyebrow">Project to lead with</p>
                  <h3>{interviewPrep.recommended_project.name}</h3>
                  <p>{interviewPrep.recommended_project.why}</p>
                  <strong>Learn before the call</strong>
                  <div className="keyword-row">
                    {interviewPrep.recommended_project.learn_next.map((item) => <span key={item}>{item}</span>)}
                  </div>
                </article>
                <article className="qa-grid">
                  <div>
                    <p className="eyebrow">HR round</p>
                    {interviewPrep.hr_round.map((item) => (
                      <details className="qa-card" key={item.question}>
                        <summary>{item.question}</summary>
                        <p>{item.answer}</p>
                      </details>
                    ))}
                  </div>
                  <div>
                    <p className="eyebrow">Technical round</p>
                    {interviewPrep.technical_round.map((item) => (
                      <details className="qa-card" key={item.question}>
                        <summary>{item.question}</summary>
                        <p>{item.answer}</p>
                      </details>
                    ))}
                  </div>
                  <div>
                    <p className="eyebrow">Technical round 2 advanced</p>
                    {interviewPrep.technical_round_2_advanced.map((item) => (
                      <details className="qa-card" key={item.question}>
                        <summary>{item.question}</summary>
                        <p>{item.answer}</p>
                      </details>
                    ))}
                  </div>
                  <div>
                    <p className="eyebrow">Final HR and negotiation</p>
                    {interviewPrep.final_hr_round.map((item) => (
                      <details className="qa-card" key={item.question}>
                        <summary>{item.question}</summary>
                        <p>{item.answer}</p>
                      </details>
                    ))}
                  </div>
                </article>
                {interviewPrep.github_project_focus.length > 0 ? (
                  <article className="insight-block">
                    <p className="eyebrow">GitHub README evidence</p>
                    <div className="project-evidence-list">
                      {interviewPrep.github_project_focus.map((project) => (
                        <div className="project-evidence" key={project.repo}>
                          <a href={project.url} rel="noreferrer" target="_blank">{project.repo}</a>
                          <p>{project.summary}</p>
                          <div className="keyword-row">
                            {project.skills.slice(0, 8).map((skill) => <span key={`${project.repo}-${skill}`}>{skill}</span>)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </article>
                ) : null}
                <article className="insight-block">
                  <p className="eyebrow">Market talking points</p>
                  <ul className="brief-list">
                    {interviewPrep.talking_points.map((point) => <li key={point}>{point}</li>)}
                  </ul>
                  {interviewPrep.readme_context_note ? <small>{interviewPrep.readme_context_note}</small> : null}
                </article>
              </div>
            ) : (
              <div className="empty-state">
                <h3>Starts when an interview reaches you</h3>
                <p>Click Interview on a job card after a recruiter or hiring manager reaches out. Then this section builds role-specific questions, STAR answers, project focus, and learning priorities.</p>
              </div>
            )}
          </section>
        ) : null}

        {activeTab === "Insights" ? (
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Market intelligence</p>
                <h2>Insights</h2>
              </div>
              <button disabled={isLoadingStrategy || !canUseLiveApp} onClick={handleLoadCareerStrategy}>
                <Lightbulb size={18} />
                {isLoadingStrategy ? "Generating..." : "Generate strategy"}
              </button>
            </div>
            <div className="status-grid">
              <div className="status-column"><h3>Visible jobs</h3><strong>{filteredJobs.length}</strong></div>
              <div className="status-column"><h3>Best score</h3><strong>{topJob ? topJob.score : 0}</strong></div>
              <div className="status-column"><h3>Average fit</h3><strong>{topJobs.length ? avgScore : 0}</strong></div>
              <div className="status-column"><h3>Applied</h3><strong>{filteredJobs.filter((job) => job.status === "applied").length}</strong></div>
            </div>
            {careerStrategy ? (
              <div className="strategy-board">
                <article className="prep-hero">
                  <p className="eyebrow">Career strategist</p>
                  <h3>{careerStrategy.headline}</h3>
                  <p>Current best job: {careerStrategy.current_best_job}</p>
                </article>
                <div className="role-table">
                  {careerStrategy.top_roles.slice(0, 10).map((role) => (
                    <article className="role-row" key={role.role}>
                      <div>
                        <strong>{role.role}</strong>
                        <span>{role.category} · {role.salary} · Visa: {role.visa}</span>
                      </div>
                      <div className="score-badge">{role.match}</div>
                    </article>
                  ))}
                </div>
                <div className="strategy-grid">
                  {Object.entries(careerStrategy.company_tiers).map(([tier, companies]) => (
                    <article className="insight-block" key={tier}>
                      <h3>{tier}</h3>
                      <div className="keyword-row">
                        {companies.slice(0, 12).map((company) => <span key={company}>{company}</span>)}
                      </div>
                    </article>
                  ))}
                </div>
                <article className="insight-block">
                  <h3>Next actions</h3>
                  <ul className="brief-list">
                    {careerStrategy.next_actions.map((action) => <li key={action}>{action}</li>)}
                  </ul>
                  <p>{careerStrategy.fastest_path_120k}</p>
                </article>
              </div>
            ) : (
              <div className="empty-state tab-list">
                <h3>No strategy generated yet</h3>
                <p>Click Generate strategy to use OpenAI when configured, with a deterministic fallback if the API is unavailable.</p>
              </div>
            )}
          </section>
        ) : null}

        {activeTab === "Settings" ? (
          <section className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Configuration</p>
                <h2>Settings</h2>
              </div>
            </div>
            <ul className="brief-list">
              <li>Backend API: {isApiConfigured ? "connected" : "not configured"}</li>
              <li>Auth mode: {isAuthRequired ? "private sign-in" : "temporary public live mode"}</li>
              <li>Country filter: {countryFilter} with backend and frontend filtering</li>
              <li>PDF compiler: {compiler?.available ? "latexmk available" : "latexmk unavailable or not checked"}</li>
              <li>Discovery: dashboard button plus twice-daily GitHub Actions scheduler</li>
            </ul>
          </section>
        ) : null}

        {activeTab === "Dashboard" ? (
        <section className="dashboard-grid">
          <div className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Australian market pulse</p>
                <h2>Target roles released by month</h2>
              </div>
              <span className="health-pill good">{filteredJobs.length} tracked roles</span>
            </div>
            <div className="market-chart" aria-label="Monthly target role releases">
              {monthlyRoleReleases.map((month) => (
                <div className="market-chart__month" key={month.key}>
                  <button
                    aria-label={`Show ${month.total} jobs in ${month.label}`}
                    className={selectedMonth?.key === month.key ? "market-chart__bar-wrap selected" : "market-chart__bar-wrap"}
                    onClick={() => setSelectedMonthKey(month.key)}
                    type="button"
                  >
                    <div
                      className="market-chart__bar"
                      style={{ height: `${Math.max(8, (month.total / maxMonthlyReleases) * 100)}%` }}
                      title={`${month.total} roles in ${month.label}`}
                    >
                      <span>{month.total}</span>
                    </div>
                  </button>
                  <strong>{month.label}</strong>
                </div>
              ))}
            </div>
            <div className="role-family-grid">
              {Object.entries(
                monthlyRoleReleases.reduce<Record<string, number>>((totals, month) => {
                  Object.entries(month.families).forEach(([family, count]) => {
                    totals[family] = (totals[family] ?? 0) + count;
                  });
                  return totals;
                }, {})
              ).map(([family, count]) => (
                <span key={family}>{family}: {count}</span>
              ))}
            </div>
            <div className="month-drilldown">
              <div className="section-heading compact">
                <div>
                  <p className="eyebrow">Month drill-down</p>
                  <h3>{selectedMonth?.label ?? "Selected"} jobs</h3>
                </div>
                <span className="health-pill">{selectedMonthJobs.length} roles</span>
              </div>
              <div className="job-list compact-list">
                {selectedMonthJobs.length > 0 ? selectedMonthJobs.map(renderJobCard) : (
                  <div className="empty-state">
                    <h3>No jobs in this month yet</h3>
                    <p>When the scheduler discovers roles with this posted month, they will appear here.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Priority queue</p>
                <h2>Recommended jobs</h2>
              </div>
              <button disabled={isDiscovering || !canUseLiveApp} onClick={handleDiscoverJobs}>
                {isDiscovering ? "Discovering..." : "Discover jobs"}
              </button>
            </div>
            <div className="job-list">
              {topJobs.length === 0 ? (
                <div className="empty-state">
                  <h3>No live jobs yet</h3>
                  <p>Click Discover jobs to pull fresh listings, or paste a job description above.</p>
                </div>
              ) : null}
              {visibleJobs.map(renderJobCard)}
            </div>
          </div>

          <div className="side-stack">
            {draft ? (
              <section className="panel draft-panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">{draft.channel} draft</p>
                    <h2>{draft.subject}</h2>
                  </div>
                </div>
                <textarea readOnly value={draft.body} />
                <div className="inline-controls">
                  <button onClick={handleCopyDraft}>
                    <Copy size={16} />
                    {draftCopied ? "Copied!" : "Copy"}
                  </button>
                  {draft.download_url ? <button onClick={() => openDownload(draft.download_url)}>Download</button> : null}
                  <small>Draft only. Review, edit, then send manually.</small>
                </div>
              </section>
            ) : null}

            <section className="panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">CRM</p>
                  <h2>Recruiter follow-ups</h2>
                </div>
                <button>Reach out</button>
              </div>
              <div className="recruiter-list">
                {(isDemoMode ? mockRecruiters : []).map((recruiter) => (
                  <article className="recruiter-row" key={recruiter.id}>
                    <div>
                      <strong>{recruiter.name}</strong>
                      <span>{recruiter.company}</span>
                      <small>{recruiter.focus_area}</small>
                    </div>
                    <div className="quality">{recruiter.quality_score}</div>
                  </article>
                ))}
                {!isDemoMode ? (
                  <div className="empty-state">
                    <h3>No live recruiters yet</h3>
                    <p>Add recruiter records after your first outreach cycle.</p>
                  </div>
                ) : null}
              </div>
            </section>

            <section className="panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Evening digest</p>
                  <h2>Next AI brief</h2>
                </div>
                <Clock3 size={18} />
              </div>
              <ul className="brief-list">
                <li>Jobs discovered and deduplicated</li>
                <li>Resume strategies needing review</li>
                <li>NEM/BESS interview talking points</li>
                <li>Recruiter emails held for approval</li>
              </ul>
            </section>
          </div>
        </section>
        ) : null}
      </section>
    </main>
  );
}
