"use client";
import React from "react";
import { BackgroundBeams } from "./components/ui/background-beams.jsx";
import App from "./App";

export function BackgroundBeam() {
  return (
    (<div className="h-screen w-screen">
    <div
      className="h-[40rem] w-full rounded-md bg-neutral-950 relative flex flex-col items-center justify-center antialiased">
      {/* <App /> */}
      <BackgroundBeams />
    </div>
    </div>)
  );
}
