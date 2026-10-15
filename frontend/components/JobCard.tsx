import { ExternalLink, FileText, Mail, MessageSquare, Mic, Star, Target, X } from "lucide-react";
import type { Job, JobStatus } from "../lib/types";

type JobCardProps = {
  job: Job;
  isBusy?: boolean;
  onApply?: (job: Job) => void;
  onGenerateCover?: (job: Job) => void;
  onGenerateResume?: (job: Job) => void;
  onGenerateOutreach?: (job: Job) => void;
  onGenerateSkillGap?: (job: Job) => void;
  onGenerateInterviewPrep?: (job: Job) => void;
  onUpdateStatus?: (job: Job, status: JobStatus) => void;
};

export function JobCard({
  job,
  isBusy,
  onApply,
  onGenerateCover,
  onGenerateResume,
  onGenerateOutreach,
  onGenerateSkillGap,
  onGenerateInterviewPrep,
  onUpdateStatus
}: JobCardProps) {
  const salary = job.score_breakdown.salary_estimate
    ?? (job.salary_min && job.salary_max ? `Listed range: $${job.salary_min.toLocaleString()}-$${job.salary_max.toLocaleString()}` : "Salary: estimate after scoring");

  return (
    <article className="job-card">
      <div className="job-card__header">
        <div>
          <p className="eyebrow">{job.company}</p>
          <h3>{job.title}</h3>
          <span>{job.location}</span>
          <div className="job-meta">
            <small className="status-pill">{job.status}</small>
            <small>{salary}</small>
          </div>
        </div>
        <div className={`score-badge ${job.score >= 70 ? "score-badge--high" : job.score >= 40 ? "score-badge--medium" : "score-badge--low"}`}>
          {job.score}
        </div>
      </div>
      <p className="recommendation">{job.score_breakdown.recommended_action}</p>
      <p className="project">Highlight: {job.score_breakdown.best_project_to_highlight}</p>
      <div className="keyword-row">
        {(job.score_breakdown.missing_keywords ?? []).slice(0, 4).map((keyword) => (
          <span key={keyword}>{keyword}</span>
        ))}
      </div>
      <div className="action-row" aria-label={`Actions for ${job.title}`}>
        <button disabled={isBusy} onClick={() => onGenerateResume?.(job)} title="Generate resume"><FileText size={18} />Resume</button>
        <button disabled={isBusy} onClick={() => onGenerateCover?.(job)} title="Generate cover letter"><Mail size={18} />Cover</button>
        <button disabled={isBusy} onClick={() => onGenerateSkillGap?.(job)} title="Analyse skill gap"><Target size={18} />Skill Gap</button>
        <button disabled={isBusy} onClick={() => onGenerateOutreach?.(job)} title="Generate outreach"><MessageSquare size={18} />Reach Out</button>
        <button disabled={isBusy} onClick={() => onGenerateInterviewPrep?.(job)} title="Generate interview prep after interview contact"><Mic size={18} />Interview</button>
        <button disabled={isBusy} onClick={() => onUpdateStatus?.(job, "saved")} title="Save job"><Star size={18} />Save</button>
        <button disabled={isBusy || !job.url} onClick={() => onApply?.(job)} title="Open apply link"><ExternalLink size={18} />Apply</button>
        <button disabled={isBusy} className="ghost" onClick={() => onUpdateStatus?.(job, "ignored")} title="Ignore job"><X size={18} />Ignore</button>
      </div>
    </article>
  );
}
