import api from "./api";

export type InterviewHistoryItem = {
  session_id: string;
  category: string;
  presentation_type: string | null;
  finished: boolean;
  answered_count: number;
  created_at: string;
};

export async function listInterviewHistory(): Promise<InterviewHistoryItem[]> {
  const { data } = await api.get<InterviewHistoryItem[]>("/interviews/history");
  return data;
}
