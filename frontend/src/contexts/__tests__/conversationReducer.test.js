import { conversationReducer } from "../conversationReducer";

const reduce = (state, action) => conversationReducer(state, action);

test("adds a new message", () => {
  const next = reduce([], {
    type: "add",
    message: { role: "user", content: "Hi" },
  });

  expect(next).toEqual([{ role: "user", content: "Hi" }]);
});

test("starts and updates assistant message", () => {
  const state = [
    { role: "user", content: "Hi" },
    { role: "assistant", content: "" },
  ];
  const started = reduce(state, { type: "start_assistant_message" });
  const updated = reduce(started, {
    type: "update_last_assistant",
    content: "Hello",
  });

  expect(updated[updated.length - 1].content).toBe("Hello");
});

test("replaces history", () => {
  const next = reduce(
    [{ role: "user", content: "Old" }],
    { type: "replace", history: [{ role: "user", content: "New" }] }
  );

  expect(next).toEqual([{ role: "user", content: "New" }]);
});
