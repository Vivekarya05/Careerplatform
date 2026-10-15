import type { Job, Recruiter } from "./types";

export const mockJobs: Job[] = [
  {
    id: "1",
    title: "BESS Trading Analyst",
    company: "TagEnergy",
    location: "Sydney, NSW",
    source: "company",
    status: "new",
    score: 92,
    score_breakdown: {
      interview_probability: 66,
      recommended_action: "Prioritise today",
      best_project_to_highlight: "NEM Market Intelligence & BESS Trading Platform",
      missing_keywords: ["PLEXOS"]
    }
  },
  {
    id: "2",
    title: "Graduate Energy Market Analyst",
    company: "AEMO",
    location: "Melbourne, VIC",
    source: "seek",
    status: "saved",
    score: 95,
    score_breakdown: {
      interview_probability: 70,
      recommended_action: "Prioritise today",
      best_project_to_highlight: "AEMO NEMWeb ETL Pipeline",
      missing_keywords: []
    }
  },
  {
    id: "3",
    title: "Power BI Analyst",
    company: "Energy Consultancy",
    location: "Hybrid",
    source: "indeed",
    status: "new",
    score: 78,
    score_breakdown: {
      interview_probability: 56,
      recommended_action: "Apply this week",
      best_project_to_highlight: "PostgreSQL + Power BI energy analytics dashboard",
      missing_keywords: ["FCAS", "BESS"]
    }
  }
];

export const mockRecruiters: Recruiter[] = [
  {
    id: "r1",
    name: "Sarah Lee",
    company: "Energy Search Partners",
    focus_area: "BESS and trading analytics",
    relationship_stage: "reached_out",
    response_status: "waiting",
    followup_due: "Today",
    quality_score: 82
  },
  {
    id: "r2",
    name: "Daniel Nguyen",
    company: "Renewables Talent AU",
    focus_area: "Graduate energy analytics",
    relationship_stage: "new",
    response_status: "not contacted",
    followup_due: "Tomorrow",
    quality_score: 76
  }
];

