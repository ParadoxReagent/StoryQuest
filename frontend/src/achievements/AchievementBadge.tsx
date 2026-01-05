import { motion } from 'framer-motion';
import { Achievement } from './types';
import { TIER_COLORS } from './definitions';

interface AchievementBadgeProps {
  achievement: Omit<Achievement, 'unlockedAt'>;
  isUnlocked: boolean;
  delay?: number;
}

export const AchievementBadge: React.FC<AchievementBadgeProps> = ({
  achievement,
  isUnlocked,
  delay = 0,
}) => {
  const tierColors = TIER_COLORS[achievement.tier];

  return (
    <motion.div
      className={`achievement-badge ${isUnlocked ? 'unlocked' : 'locked'}`}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.3 }}
      whileHover={isUnlocked ? { scale: 1.05 } : undefined}
      style={
        {
          '--tier-border': tierColors.border,
          '--tier-bg': tierColors.background,
          '--tier-glow': tierColors.glow,
        } as React.CSSProperties
      }
    >
      {/* Medallion shape */}
      <div className="badge-medallion">
        <span className={`badge-icon ${isUnlocked ? '' : 'grayscale'}`}>
          {isUnlocked ? achievement.icon : '?'}
        </span>
      </div>

      {/* Name */}
      <p className="badge-name">{isUnlocked ? achievement.name : '???'}</p>

      {/* Tooltip on hover (for unlocked) */}
      {isUnlocked && (
        <div className="badge-tooltip">
          <p>{achievement.description}</p>
        </div>
      )}
    </motion.div>
  );
};
