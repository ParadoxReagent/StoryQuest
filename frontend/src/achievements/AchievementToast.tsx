import { motion } from 'framer-motion';
import { Achievement } from './types';
import { TIER_COLORS } from './definitions';

interface AchievementToastProps {
  achievement: Achievement;
  toastId: string | number;
}

export const AchievementToast: React.FC<AchievementToastProps> = ({
  achievement,
}) => {
  const tierColors = TIER_COLORS[achievement.tier];

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ type: 'spring', damping: 20, stiffness: 300 }}
      className="achievement-toast"
      style={{
        background: `linear-gradient(145deg, ${tierColors.background}, #fcf9f2)`,
        border: `3px solid ${tierColors.border}`,
        boxShadow: `
          0 8px 32px rgba(0, 0, 0, 0.2),
          0 0 20px ${tierColors.glow},
          inset 0 1px 0 rgba(255, 255, 255, 0.5)
        `,
      }}
    >
      {/* Sparkle overlay */}
      <div className="achievement-toast-sparkles" />

      {/* Badge icon */}
      <motion.div
        className="achievement-toast-icon"
        animate={{
          rotate: [0, -10, 10, -5, 5, 0],
          scale: [1, 1.2, 1.1, 1.15, 1],
        }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <span className="text-3xl">{achievement.icon}</span>
      </motion.div>

      {/* Content */}
      <div className="achievement-toast-content">
        <motion.p
          className="achievement-toast-label"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          Achievement Unlocked!
        </motion.p>
        <motion.h3
          className="achievement-toast-title"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          {achievement.name}
        </motion.h3>
        <motion.p
          className="achievement-toast-description"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {achievement.description}
        </motion.p>
      </div>
    </motion.div>
  );
};
