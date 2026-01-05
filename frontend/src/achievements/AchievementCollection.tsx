import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Achievement } from './types';
import { ACHIEVEMENTS, TIER_COLORS, TIER_NAMES, TIER_ORDER } from './definitions';
import { AchievementBadge } from './AchievementBadge';

interface AchievementCollectionProps {
  isOpen: boolean;
  onClose: () => void;
  unlockedAchievements: Achievement[];
  onReset?: () => void;
}

export const AchievementCollection: React.FC<AchievementCollectionProps> = ({
  isOpen,
  onClose,
  unlockedAchievements,
  onReset,
}) => {
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const unlockedIds = new Set(unlockedAchievements.map((a) => a.id));

  const handleReset = () => {
    if (onReset) {
      onReset();
      setShowResetConfirm(false);
    }
  };

  const achievementsByTier = TIER_ORDER.map((tier) => ({
    tier,
    achievements: Object.values(ACHIEVEMENTS).filter((a) => a.tier === tier),
  }));

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="achievement-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            className="achievement-modal"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="achievement-modal-title"
          >
            {/* Header */}
            <div className="achievement-modal-header">
              <h2 id="achievement-modal-title" className="achievement-modal-title">
                Your Achievements
              </h2>
              <p className="achievement-modal-subtitle">
                {unlockedAchievements.length} of {Object.keys(ACHIEVEMENTS).length}{' '}
                unlocked
              </p>
              <button
                onClick={onClose}
                className="achievement-close-btn"
                aria-label="Close achievements"
              >
                {'\u2715'}
              </button>
            </div>

            {/* Badge grid by tier */}
            <div className="achievement-modal-content">
              {achievementsByTier.map(({ tier, achievements }) => (
                <div key={tier} className="achievement-tier-section">
                  <h3
                    className="achievement-tier-title"
                    style={{ color: TIER_COLORS[tier].border }}
                  >
                    {TIER_NAMES[tier]}
                  </h3>
                  <div className="achievement-grid">
                    {achievements.map((achievement, index) => (
                      <AchievementBadge
                        key={achievement.id}
                        achievement={achievement}
                        isUnlocked={unlockedIds.has(achievement.id)}
                        delay={index * 0.05}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Footer with reset button */}
            {onReset && (
              <div className="achievement-modal-footer">
                <AnimatePresence mode="wait">
                  {!showResetConfirm ? (
                    <motion.button
                      key="reset-btn"
                      className="achievement-reset-btn"
                      onClick={() => setShowResetConfirm(true)}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      Reset Progress
                    </motion.button>
                  ) : (
                    <motion.div
                      key="confirm"
                      className="achievement-reset-confirm"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                    >
                      <p>Are you sure? This cannot be undone.</p>
                      <div className="achievement-reset-actions">
                        <button
                          className="achievement-reset-cancel"
                          onClick={() => setShowResetConfirm(false)}
                        >
                          Cancel
                        </button>
                        <button
                          className="achievement-reset-confirm-btn"
                          onClick={handleReset}
                        >
                          Yes, Reset
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
