import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const isAuthRequired = process.env.NEXT_PUBLIC_REQUIRE_AUTH !== "false";
export const isAuthConfigured = isAuthRequired && Boolean(supabaseUrl && supabaseAnonKey);

export const supabase = isAuthConfigured
  ? createClient(supabaseUrl as string, supabaseAnonKey as string)
  : null;
