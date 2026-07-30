import { Link } from "react-router-dom";

function AnimatedText({ text, delayOffset = 0 }: { text: string; delayOffset?: number }) {
  return (
    <span className="letter-write" aria-label={text}>
      {Array.from(text).map((letter, index) => {
        const variedDelay = delayOffset + ((index * 37 + letter.charCodeAt(0) * 13) % 71) / 100;
        return <span aria-hidden="true" key={`${letter}-${index}`} style={{ animationDelay: `${variedDelay}s` }}>{letter === " " ? "\u00a0" : letter}</span>;
      })}
    </span>
  );
}

export function WelcomePage() {
  return (
    <main className="map-page welcome-page">
      <div className="map-grain" aria-hidden="true" />
      <div className="map-border" aria-hidden="true" />

      <header className="map-header ink-reveal">
        <span className="eyebrow"><AnimatedText text="A gathering place for readers" /></span>
        <p className="map-mark"><AnimatedText text="T." delayOffset={.12} /></p>
      </header>

      <section className="welcome-content" aria-labelledby="welcome-title">
        <h1 id="welcome-title" className="welcome-title"><AnimatedText text="Tomeys" delayOffset={.18} /></h1>
        <div className="title-ornament ink-reveal ink-reveal-delay" aria-hidden="true">
          <span />
          <i>✦</i>
          <span />
        </div>
        <p className="welcome-message ink-reveal ink-reveal-delay">
          <AnimatedText text="What up Tomey? Create an account or log in to continue your journey." delayOffset={.34} />
        </p>
        <Link className="ink-button ink-reveal ink-reveal-delay" to="/auth">
          <AnimatedText text="Join the club" delayOffset={.56} />
          <span aria-hidden="true">→</span>
        </Link>
      </section>

      <footer className="map-footer ink-reveal ink-reveal-delay">
        <span><AnimatedText text="Gather" delayOffset={.3} /></span>
        <i aria-hidden="true">·</i>
        <span><AnimatedText text="Read" delayOffset={.48} /></span>
        <i aria-hidden="true">·</i>
        <span><AnimatedText text="Remember" delayOffset={.64} /></span>
      </footer>
    </main>
  );
}
