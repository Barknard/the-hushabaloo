/**
 * Silence every test run.
 *
 * The suite exercises real playback -- that is the point, it is how pause/resume
 * and the karaoke timing get verified -- but it also means running the tests
 * plays the book out loud through the machine's speakers.
 *
 * Muting the element rather than setting volume to 0 keeps `.volume` readable,
 * which the ambient-bed test asserts on.
 */
export const MUTE_ALL_AUDIO = () => {
  const play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function (...args) {
    this.muted = true;
    return play.apply(this, args);
  };
};
