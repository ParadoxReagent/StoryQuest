import { motion } from 'framer-motion';

interface AchievementTriggerProps {
  unlockedCount: number;
  totalCount: number;
  onClick: () => void;
}

export const AchievementTrigger: React.FC<AchievementTriggerProps> = ({
  unlockedCount,
  totalCount,
  onClick,
}) => {
  const hasAchievements = unlockedCount > 0;

  return (
    <motion.button
      onClick={onClick}
      className="achievement-trigger"
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      title="View your achievements"
      aria-label={`View achievements: ${unlockedCount} of ${totalCount} unlocked`}
    >
      {/* Medal icon */}
      <span className="achievement-trigger-icon">{'\u{1F3C5}'}</span>

      {/* Badge count */}
      <span className="achievement-count">
        {unlockedCount}/{totalCount}
      </span>

      {/* Glow pulse when achievements unlocked */}
      {hasAchievements && (
        <motion.div
          className="achievement-trigger-glow"
          animate={{
            opacity: [0.3, 0.6, 0.3],
            scale: [1, 1.15, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      )}
    </motion.button>
  );
};
