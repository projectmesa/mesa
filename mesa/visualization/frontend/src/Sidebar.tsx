import React, { useEffect, useState } from "react";
import { initGUI } from "./initGUI";

type SidebarProps = {
  modelParams: any;
  send: (data: any) => void;
};

export const Sidebar = ({ modelParams, send }: SidebarProps) => {
  useEffect(() => {
    initGUI(modelParams, send);

    return () => {
      document.getElementById("sidebar")!.innerHTML = "";
    };
  }, [modelParams]);

  return <div className="col-xl-4 col-lg-4 col-md-4 col-3" id="sidebar"></div>;
};
