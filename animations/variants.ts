export const motionTokens = {
  duration: {
    fast: 0.15,
    normal: 0.3,
    slow: 0.6,
    dramatic: 1.2,
  },
  ease: {
    default: [0.4, 0, 0.2, 1] as const,
    spring: { type: "spring" as const, stiffness: 300, damping: 30 },
    bounce: [0.34, 1.56, 0.64, 1] as const,
  },
};

export const heroEyebrow = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: motionTokens.ease.default },
  },
};

export const heroTitle = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: motionTokens.ease.default, delay: 0.05 },
  },
};

export const heroSubtitle = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: motionTokens.ease.default, delay: 0.15 },
  },
};

export const heroBody = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: motionTokens.ease.default, delay: 0.2 },
  },
};

export const heroCta = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.5, ease: motionTokens.ease.default, delay: 0.3 },
  },
};

export const sectionReveal = {
  hidden: { opacity: 0, y: 32 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: motionTokens.ease.default },
  },
};

export const cardsContainer = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08 },
  },
};

export const cardItem = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: motionTokens.ease.default },
  },
};
