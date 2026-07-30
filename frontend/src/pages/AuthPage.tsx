import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { googleLogin, login, register } from "../lib/api";

declare global {
  interface Window { google?: { accounts: { id: { initialize: (config: { client_id: string; callback: (response: { credential: string }) => void }) => void; renderButton: (element: HTMLElement, options: { theme: string; size: string; width: number; text: string }) => void } } }; }
}

export function AuthPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

  async function googleSignIn(credential: string) {
    setError(""); setIsSubmitting(true);
    try {
      const token = await googleLogin(credential);
      localStorage.setItem("tomeys_token", token.access_token);
      navigate("/dashboard");
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Google sign-in could not be completed."); } finally { setIsSubmitting(false); }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const password = String(data.get("password") || "");
    setError(""); setIsSubmitting(true);
    try {
      if (mode === "register") await register({ username: String(data.get("username")), email: String(data.get("email")), password, display_name: String(data.get("displayName")) });
      const token = await login(mode === "register" ? String(data.get("email")) : String(data.get("identity")), password);
      localStorage.setItem("tomeys_token", token.access_token);
      navigate("/dashboard");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to continue right now.");
    } finally { setIsSubmitting(false); }
  }

  return <main className="map-page auth-page">
    <div className="map-grain" aria-hidden="true" />
    <div className="map-border" aria-hidden="true" />
    <section className="auth-content ink-reveal" aria-labelledby="auth-title">
      <p className="eyebrow">The next chapter awaits</p>
      <h1 id="auth-title">{mode === "login" ? "Welcome back, Tomey!" : "Make your mark."}</h1>
      <p className="auth-intro">{mode === "login" ? "Sign in and pick up where the last chapter left off." : "Create your reader profile and join the conversation."}</p>
      <div className="auth-tabs"><button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Sign in</button><button type="button" className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Create account</button></div>
        <form className="auth-form" onSubmit={submit}>
        {mode === "register" && <><label>Display name<input name="displayName" required placeholder="How readers know you" /></label><label>Username<input name="username" required placeholder="yourhandle" /></label><label>Email<input type="email" name="email" required placeholder="you@example.com" /></label></>}
        {mode === "login" && <label>Email or username<input name="identity" required autoComplete="username" placeholder="you@example.com" /></label>}
        <label>Password<input type="password" name="password" required minLength={8} autoComplete={mode === "login" ? "current-password" : "new-password"} placeholder="At least 8 characters" /></label>
        {error && <p className="form-error" role="alert">{error}</p>}
          <button type="submit" className="ink-button form-submit" disabled={isSubmitting}>{isSubmitting ? "Opening your chapter…" : mode === "login" ? "Sign in" : "Create account"}<span aria-hidden="true">→</span></button>
        </form>
        <div className="auth-divider"><span>or continue with</span></div>
        {googleClientId ? <GoogleButton clientId={googleClientId} onCredential={googleSignIn} /> : <p className="google-config-note">Add <code>VITE_GOOGLE_CLIENT_ID</code> to enable Google sign-in.</p>}
        <Link className="text-link" to="/">← Return to Tomeys</Link>
    </section>
  </main>;
}

function GoogleButton({ clientId, onCredential }: { clientId: string; onCredential: (credential: string) => void }) {
  const [element, setElement] = useState<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!element) return;
    const render = () => {
      if (!window.google) return;
      window.google.accounts.id.initialize({ client_id: clientId, callback: ({ credential }) => onCredential(credential) });
      window.google.accounts.id.renderButton(element, { theme: "outline", size: "large", width: 400, text: "continue_with" });
    };
    if (window.google) { render(); return; }
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client"; script.async = true;
    script.onload = render;
    document.head.appendChild(script);
  }, [clientId, element, onCredential]);
  return <div className="google-button" ref={setElement} />;
}
