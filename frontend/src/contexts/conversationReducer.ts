export interface Message {
  role: 'user' | 'assistant' | 'model';
  content: string;
}

export type ConversationAction =
  | { type: 'reset' }
  | { type: 'replace'; history: Message[] }
  | { type: 'add'; message: Message }
  | { type: 'start_assistant_message' }
  | { type: 'update_last_assistant'; content: string };

const findLastAssistantIndex = (messages: Message[]): number => {
  for (let i = messages.length - 1; i >= 0; i -= 1) {
    if (messages[i].role === "assistant" || messages[i].role === "model") {
      return i;
    }
  }
  return -1;
};

export const conversationReducer = (state: Message[], action: ConversationAction): Message[] => {
  switch (action.type) {
    case "reset":
      return [];
    case "replace":
      return Array.isArray(action.history) ? action.history : state;
    case "add":
      return [...state, action.message];
    case "start_assistant_message": {
      const filtered = state.filter((msg) => msg.content !== "");
      return [...filtered, { role: "assistant", content: "" }];
    }
    case "update_last_assistant": {
      const index = findLastAssistantIndex(state);
      if (index === -1) return state;
      const next = [...state];
      next[index] = { ...next[index], content: action.content };
      return next;
    }
    default:
      return state;
  }
};