import { motion } from "framer-motion";

export default function TypingIndicator() {
  return (
    <div className="flex w-fit items-center gap-1 rounded-2xl bg-white px-4 py-3 shadow-sm">
      {[0, 1, 2].map((index) => (
        <motion.span
          key={index}
          className="h-2 w-2 rounded-full bg-teal-500"
          animate={{ y: [0, -5, 0], opacity: [0.45, 1, 0.45] }}
          transition={{ repeat: Infinity, duration: 0.9, delay: index * 0.15 }}
        />
      ))}
    </div>
  );
}
