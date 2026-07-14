export const SEVERITIES = {
  CRITICAL: {
    label: "CRITICAL",
    color: "var(--severity-critical)",
    bgColor: "rgba(239, 68, 68, 0.15)",
    textColor: "#FCA5A5",
    borderColor: "rgba(239, 68, 68, 0.4)",
  },
  HIGH: {
    label: "HIGH",
    color: "var(--severity-high)",
    bgColor: "rgba(249, 115, 22, 0.15)",
    textColor: "#FED7AA",
    borderColor: "rgba(249, 115, 22, 0.4)",
  },
  MEDIUM: {
    label: "MEDIUM",
    color: "var(--severity-medium)",
    bgColor: "rgba(234, 179, 8, 0.15)",
    textColor: "#FEF08A",
    borderColor: "rgba(234, 179, 8, 0.4)",
  },
  LOW: {
    label: "LOW",
    color: "var(--severity-low)",
    bgColor: "rgba(34, 197, 94, 0.15)",
    textColor: "#BBF7D0",
    borderColor: "rgba(34, 197, 94, 0.4)",
  },
  NONE: {
    label: "NORMAL",
    color: "var(--severity-none)",
    bgColor: "rgba(100, 116, 139, 0.15)",
    textColor: "#E2E8F0",
    borderColor: "rgba(100, 116, 139, 0.4)",
  },
};

export const getSeverityByRisk = (risk) => {
  if (!risk) return SEVERITIES.NONE;
  const riskUpper = risk.toUpperCase();
  if (riskUpper === "HIGH") return SEVERITIES.HIGH; // Default mapping
  if (riskUpper === "MEDIUM") return SEVERITIES.MEDIUM;
  if (riskUpper === "LOW") return SEVERITIES.LOW;
  return SEVERITIES.NONE;
};

// Maps situation name to severity overrides
export const getSeverity = (situation, risk) => {
  if (situation === "Weapon Detected" || situation === "Fall Detected") {
    return SEVERITIES.CRITICAL;
  }
  return getSeverityByRisk(risk);
};

export const DETECTOR_COLORS = {
  person: "#3B82F6",    // Accent Blue
  phone: "#06B6D4",     // Accent Cyan
  laptop: "#10B981",    // Green
  bag: "#F59E0B",       // Orange
  bottle: "#8B5CF6",    // Purple
  knife: "#EF4444",     // Crimson Red
  bicycle: "#EAB308",   // Yellow
  motorcycle: "#EAB308",// Yellow
  animal: "#14B8A6",    // Teal
  default: "#E2E8F0"
};
