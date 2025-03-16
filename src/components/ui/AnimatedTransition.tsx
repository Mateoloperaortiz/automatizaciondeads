
import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';

type AnimationType = 'fade' | 'slide-up' | 'slide-down' | 'scale' | 'blur';

interface AnimatedTransitionProps {
  children: ReactNode;
  type?: AnimationType;
  duration?: number;
  delay?: number;
  className?: string;
}

const animations = {
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  'slide-up': {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: 20, opacity: 0 },
  },
  'slide-down': {
    initial: { y: -20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 },
  },
  scale: {
    initial: { scale: 0.96, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.96, opacity: 0 },
  },
  blur: {
    initial: { filter: 'blur(8px)', opacity: 0 },
    animate: { filter: 'blur(0px)', opacity: 1 },
    exit: { filter: 'blur(8px)', opacity: 0 },
  },
};

const AnimatedTransition: React.FC<AnimatedTransitionProps> = ({
  children,
  type = 'fade',
  duration = 0.3,
  delay = 0,
  className = '',
}) => {
  const selectedAnimation = animations[type];

  return (
    <motion.div
      initial={selectedAnimation.initial}
      animate={selectedAnimation.animate}
      exit={selectedAnimation.exit}
      transition={{
        duration,
        delay,
        ease: [0.25, 0.1, 0.25, 1], // Cubic bezier curve resembling Apple's easing
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

export default AnimatedTransition;
