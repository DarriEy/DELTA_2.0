import React from "react";
import { render, screen } from "@testing-library/react";
import GeneralPanel from "../GeneralPanel";

test("renders general mode panel copy", () => {
  render(<GeneralPanel />);

  expect(screen.getByText(/Welcome Commander/i)).toBeInTheDocument();
  expect(screen.getByText(/Delta is standing by/i)).toBeInTheDocument();
});
