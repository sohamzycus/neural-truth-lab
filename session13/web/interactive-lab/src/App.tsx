import { LabPage } from "./components/lab/LabPage";

export default function App() {
  return (
    <div className="lab-shell min-h-screen bg-[#07090d] text-stone-200">
      <nav className="sticky top-0 z-50 border-b border-white/10 bg-[#07090d]/90 backdrop-blur px-4 py-3 text-xs tracking-widest text-stone-500">
        <div className="mx-auto flex max-w-5xl flex-wrap gap-4">
          <a href="#machine">Machine</a>
          <a href="#evidence">Evidence</a>
          <a href="#cockpit">Cockpit</a>
          <a href="#surprise">Surprise</a>
          <a href="#playback">Playback</a>
          <a href="#reproduce">Reproduce</a>
        </div>
      </nav>
      <LabPage />
    </div>
  );
}
