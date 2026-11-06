import { Link } from "react-router-dom";
const iconPaths = {
  search: (
    <>
      <circle cx="11" cy="11" r="6" />
      <path d="m16 16 4 4" />
    </>
  ),
  book: (
    <>
      <path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H11v17H7.5A3.5 3.5 0 0 0 4 22Z" />
      <path d="M20 5.5A3.5 3.5 0 0 0 16.5 2H13v17h3.5A3.5 3.5 0 0 1 20 22Z" />
    </>
  ),
  download: (
    <>
      <path d="M12 3v12" />
      <path d="m7 10 5 5 5-5" />
      <path d="M5 20h14" />
    </>
  ),
  arrow: (
    <>
      <path d="M5 12h14" />
      <path d="m14 7 5 5-5 5" />
    </>
  ),
  back: (
    <>
      <path d="M19 12H5" />
      <path d="m10 7-5 5 5 5" />
    </>
  ),
  brain: (
    <>
      <path d="M9 4a3 3 0 0 0-5 2.2A3 3 0 0 0 3 12a3 3 0 0 0 3 5.5V19a3 3 0 0 0 6 0V6a3 3 0 0 0-3-2Z" />
      <path d="M15 4a3 3 0 0 1 5 2.2A3 3 0 0 1 21 12a3 3 0 0 1-3 5.5V19a3 3 0 0 1-6 0V6a3 3 0 0 1 3-2Z" />
      <path d="M8 9h4M12 14H7M16 9h-4M12 14h5" />
    </>
  ),
  school: (
    <>
      <path d="m3 10 9-5 9 5-9 5Z" />
      <path d="M7 13v4c3 2 7 2 10 0v-4" />
    </>
  ),
  family: (
    <>
      <circle cx="8" cy="8" r="3" />
      <circle cx="16" cy="8" r="3" />
      <path d="M2 20c0-4 2.5-6 6-6s6 2 6 6M10 20c0-3 2-5 6-5s6 2 6 5" />
    </>
  ),
  network: (
    <>
      <circle cx="12" cy="5" r="2" />
      <circle cx="5" cy="18" r="2" />
      <circle cx="19" cy="18" r="2" />
      <path d="M11 7 6 16M13 7l5 9M7 18h10" />
    </>
  ),
  leaf: (
    <>
      <path d="M20 4c-8 0-14 4-14 11 0 3 2 5 5 5 7 0 9-8 9-16Z" />
      <path d="M5 21c3-5 7-8 12-11" />
    </>
  ),
  nodes: (
    <>
      <circle cx="5" cy="12" r="2" />
      <circle cx="12" cy="5" r="2" />
      <circle cx="19" cy="12" r="2" />
      <circle cx="12" cy="19" r="2" />
      <path d="m6.5 10.5 4-4M13.5 6.5l4 4M17.5 13.5l-4 4M10.5 17.5l-4-4" />
    </>
  ),
  grid: (
    <>
      <rect x="4" y="4" width="6" height="6" />
      <rect x="14" y="4" width="6" height="6" />
      <rect x="4" y="14" width="6" height="6" />
      <rect x="14" y="14" width="6" height="6" />
    </>
  ),
  file: (
    <>
      <path d="M6 3h8l4 4v14H6Z" />
      <path d="M14 3v5h5M9 13h6M9 17h6" />
    </>
  ),
  plus: (
    <>
      <path d="M12 5v14M5 12h14" />
    </>
  ),
  folder: (
    <>
      <path d="M3 7h7l2 2h9v10H3Z" />
    </>
  ),
  users: (
    <>
      <circle cx="9" cy="8" r="3" />
      <circle cx="17" cy="9" r="2.5" />
      <path d="M3 20c0-4 2-6 6-6s6 2 6 6M14 15c4 0 7 1.5 7 5" />
    </>
  ),
  star: (
    <path d="m12 3 2.7 5.5 6 .9-4.4 4.2 1 6-5.3-2.8-5.3 2.8 1-6-4.4-4.2 6-.9Z" />
  ),
  settings: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.4-2.4 1A8 8 0 0 0 15 6l-.3-2.6h-4L10.5 6A8 8 0 0 0 9 7.1l-2.4-1-2 3.4 2 1.5a7 7 0 0 0 0 2l-2 1.5 2 3.4 2.4-1A8 8 0 0 0 10.5 18l.2 2.6h4L15 18a8 8 0 0 0 1.5-1.1l2.4 1 2-3.4-2-1.5c.1-.3.1-.7.1-1Z" />
    </>
  ),
  eye: (
    <>
      <path d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6S2 12 2 12Z" />
      <circle cx="12" cy="12" r="2.5" />
    </>
  ),
  edit: (
    <>
      <path d="m4 20 4-.8 11-11-3.2-3.2-11 11Z" />
      <path d="m14.5 6.5 3 3" />
    </>
  ),
  upload: (
    <>
      <path d="M12 17V5" />
      <path d="m7 10 5-5 5 5" />
      <path d="M5 20h14" />
    </>
  ),
  zoomin: (
    <>
      <circle cx="10" cy="10" r="6" />
      <path d="m15 15 5 5M10 7v6M7 10h6" />
    </>
  ),
  fullscreen: (
    <>
      <path d="M8 3H3v5M16 3h5v5M8 21H3v-5M16 21h5v-5" />
    </>
  ),
};

function Icon({ name, size = 20 }) {
  return (
    <svg
      className="ui-icon"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {iconPaths[name] || iconPaths.file}
    </svg>
  );
}

function Brand({ compact = false, variant = "header" }) {
  const src = variant === "footer" ? "/footer-logo.png" : "/brand-lockup.png";
  return (
    <Link
      to="/"
      className={`brand ${compact ? "brand--compact" : ""} brand--${variant}`}
    >
      <img
        src={src}
        alt="UNIEURO · Revista Científica de Psicologia"
        className="brand-lockup"
      />
    </Link>
  );
}

function Cover({ edition, className = "" }) {
  return (
    <img
      loading={className.includes("hero-cover") ? "eager" : "lazy"}
      decoding="async"
      src={edition.cover}
      className={`cover ${className}`}
      alt={`Capa da ${edition.issue}: ${edition.title}`}
    />
  );
}

export { Icon, Brand, Cover };
