import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AuthPage } from "./pages/AuthPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ClubPage } from "./pages/ClubPage";
import { DiscoverClubsPage } from "./pages/DiscoverClubsPage";
import { BookSearchPage } from "./pages/BookSearchPage";
import { WelcomePage } from "./pages/WelcomePage";
import "./styles/global.css";

const router = createBrowserRouter([
  { path: "/", element: <WelcomePage /> },
  { path: "/auth", element: <AuthPage /> },
  { path: "/dashboard", element: <DashboardPage /> },
  { path: "/clubs/:clubId", element: <ClubPage /> },
  { path: "/clubs", element: <DiscoverClubsPage /> },
  { path: "/books", element: <BookSearchPage /> },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
