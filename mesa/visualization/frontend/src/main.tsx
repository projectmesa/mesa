import { MantineProvider } from "@mantine/core";
import * as React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <MantineProvider withNormalizeCSS>
      <App />
    </MantineProvider>
  </React.StrictMode>
);
