import React from "react";
import { render, screen } from "@testing-library/react";
import HudHeader from "../HudHeader";

test("renders HUD header branding", () => {
  render(<HudHeader dropletAvatar="/logo.png" />);

  expect(screen.getByText(/DELTA/i)).toBeInTheDocument();
  expect(screen.getByText(/Integrated Intelligence Node/i)).toBeInTheDocument();
});
