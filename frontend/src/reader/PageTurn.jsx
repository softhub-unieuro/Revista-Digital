import { motion } from "motion/react";

export function PageTurn({
  children,
  direction,
  double,
  onTurnComplete,
  pageHeight,
  pageWidth,
  renderPage,
  spreadWidth,
  turn,
}) {
  if (!turn)
    return (
      <div className="pdf-spread pdf-turn-spread" style={{ width: spreadWidth }}>
        {children}
      </div>
    );

  const forward = direction > 0;
  const basePages = !double
    ? [turn.to[0]]
    : forward
      ? [turn.from.length > 1 ? turn.from[0] : null, turn.to.at(-1)]
      : [turn.to[0], turn.from.at(-1)];
  const frontPage = !double
    ? turn.from[0]
    : forward
      ? turn.from.at(-1)
      : turn.from[0];
  const backPage = !double
    ? turn.to[0]
    : forward
      ? turn.to[0]
      : turn.to.at(-1);
  const transformOrigin = double
    ? forward
      ? "left center"
      : "right center"
    : forward
      ? "right center"
      : "left center";
  const turnId = turn.id;

  return (
    <div
      className="pdf-spread"
      style={double ? undefined : { width: pageWidth }}
    >
      {basePages.map((number, index) => (
        <div className="pdf-book-slot" key={`base-${index}`}>
          {number ? (
            renderPage(number)
          ) : (
            <div
              className="pdf-book-blank"
              style={{ width: pageWidth, height: pageHeight }}
            />
          )}
        </div>
      ))}
      <div
        className={`pdf-turn-sheet ${forward ? "turn-forward" : "turn-backward"}`}
        style={{
          left: !double ? 0 : forward ? pageWidth + 2 : 0,
          width: pageWidth,
          height: pageHeight,
        }}
      >
        <motion.div
          className="pdf-turn-flipper"
          initial={{ rotateY: 0 }}
          animate={{ rotateY: forward ? -180 : 180 }}
          transition={{
            duration: 0.48,
            ease: [0.32, 0.72, 0, 1],
          }}
          style={{ transformOrigin }}
          onAnimationComplete={() => onTurnComplete(turnId)}
        >
          <div className="pdf-turn-face pdf-turn-front">
            {renderPage(frontPage)}
          </div>
          <div className="pdf-turn-face pdf-turn-back">
            {renderPage(backPage)}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
