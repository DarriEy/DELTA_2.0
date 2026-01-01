import React from "react";
import { render, screen } from "@testing-library/react";
import HudFooter from "../HudFooter";

test("renders HUD footer telemetry", () => {
  render(<HudFooter />);

  expect(
    screen.getByText(/HYDROLOGICAL RESEARCH UNIT/i)
  ).toBeInTheDocument();
  expect(screen.getByText(/Compute/i)).toBeInTheDocument();
});
