"use client";

import { useState } from "react";
import { Sparkles, Music, Wand2, AudioLines } from "lucide-react";
import { PoetryEditor } from "@/components/PoetryEditor";
import { VoiceSelector } from "@/components/VoiceSelector";
import { GenerationModal } from "@/components/GenerationModal";
import { api } from "@/services/api";
import { Job, Project } from "@/types";

export default function StudioHomePage() {
  const [title, setTitle] = useState("دل ناداں");
  const [poetName, setPoetName] = useState("مرزا غالب");
  const [poetryText, setPoetryText] = useState(
    "دل ناداں تجھے ہوا کیا ہے\nآخر اس درد کی دوا کیا ہے"
  );

  const [engine, setEngine] = useState("f5-tts");
  const [speed, setSpeed] = useState(1.0);
  const [pitch, setPitch] = useState(0.0);
  const [speaker, setSpeaker] = useState("ur-poet-male");
  const [referenceFile, setReferenceFile] = useState<File | null>(null);

  // Job & Generation State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [jobLogs, setJobLogs] = useState<string[]>([]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleStartGeneration = async () => {
    if (!poetryText.trim()) {
      setErrorMsg("Please enter Urdu poetry verses before generating voiceover.");
      return;
    }

    setErrorMsg(null);
    setIsModalOpen(true);
    setJobLogs(["Initializing AlfaazStudio pipeline..."]);

    try {
      // 1. Create or register reference voice profile if custom audio uploaded
      let voiceId: string | undefined = undefined;
      if (referenceFile) {
        setJobLogs((prev) => [...prev, `Uploading voice reference: ${referenceFile.name}`]);
        const formData = new FormData();
        formData.append("name", `Voice-${Date.now()}`);
        formData.append("engine", engine);
        formData.append("language", "ur");
        formData.append("file", referenceFile);

        try {
          const newVoice = await api.createVoice(formData);
          voiceId = newVoice.id;
          setJobLogs((prev) => [...prev, `Voice profile created: ${newVoice.name}`]);
        } catch (err: any) {
          setJobLogs((prev) => [
            ...prev,
            `Notice: Custom voice upload skipped (${err.message}). Using preset.`,
          ]);
        }
      }

      // 2. Create Project
      setJobLogs((prev) => [...prev, `Creating project '${title}'...`]);
      const project = await api.createProject({
        title: title || "Urdu Poetry Reel",
        poet_name: poetName,
        raw_poetry: poetryText,
        voice_id: voiceId,
      });
      setCurrentProject(project);

      // 3. Trigger Audio Generation
      setJobLogs((prev) => [...prev, `Submitting audio generation task (Engine: ${engine})...`]);
      const initialJob = await api.generateAudio(project.id, {
        speed: speed,
        voice_id: voiceId,
      });
      setActiveJob(initialJob);

      // 4. Poll Job progress and logs
      const pollInterval = setInterval(async () => {
        try {
          const [updatedJob, logsRes] = await Promise.all([
            api.getJob(initialJob.id),
            api.getJobLogs(initialJob.id).catch(() => ({ logs: [] })),
          ]);

          setActiveJob(updatedJob);
          if (logsRes.logs && logsRes.logs.length > 0) {
            setJobLogs(logsRes.logs);
          }

          if (
            updatedJob.status === "completed" ||
            updatedJob.status === "failed" ||
            updatedJob.status === "cancelled"
          ) {
            clearInterval(pollInterval);
          }
        } catch {
          // Polling network glitch resilience
        }
      }, 1000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to initiate generation");
      setJobLogs((prev) => [...prev, `Error: ${err.message}`]);
    }
  };

  const handleCancelJob = async () => {
    if (activeJob) {
      try {
        await api.cancelJob(activeJob.id);
        setJobLogs((prev) => [...prev, "Cancellation requested by user."]);
      } catch (err: any) {
        console.error("Cancel failed:", err);
      }
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
      {/* Studio Header Banner */}
      <div className="mb-8 text-center sm:text-left flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-studio-border pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-studio-gold/10 border border-studio-gold/30 text-studio-gold text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Voice & Reel Studio • الفاظ اسٹوڈیو</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-studio-text tracking-tight">
            Turn Classic Urdu Poetry into Cinematic Voice-overs
          </h1>
          <p className="mt-1 text-sm text-studio-muted">
            Zero-shot voice cloning, authentic Nastaliq typesetting, and mastered acoustic ambience.
          </p>
        </div>

        <div className="flex items-center gap-3 self-center sm:self-end">
          <div className="px-3.5 py-1.5 rounded-xl bg-studio-card border border-studio-border text-xs flex items-center gap-2">
            <Music className="w-4 h-4 text-studio-emerald" />
            <span className="text-studio-muted">Cinematic DSP Active</span>
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="mb-6 p-4 rounded-xl bg-studio-rose/10 border border-studio-rose/30 text-studio-rose text-sm font-medium">
          {errorMsg}
        </div>
      )}

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Poetry Stanza Editor (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <PoetryEditor
            poetryText={poetryText}
            onChangeText={setPoetryText}
            title={title}
            onChangeTitle={setTitle}
            poetName={poetName}
            onChangePoetName={setPoetName}
          />
        </div>

        {/* Right Column: Voice & Synthesis Controls (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <VoiceSelector
            engine={engine}
            onChangeEngine={setEngine}
            speed={speed}
            onChangeSpeed={setSpeed}
            pitch={pitch}
            onChangePitch={setPitch}
            speaker={speaker}
            onChangeSpeaker={setSpeaker}
            referenceFile={referenceFile}
            onSelectReferenceFile={setReferenceFile}
          />

          {/* Mastering Summary Pill */}
          <div className="p-4 rounded-2xl bg-studio-card border border-studio-border shadow-studio flex items-center justify-between text-xs text-studio-muted">
            <div className="flex items-center gap-2">
              <AudioLines className="w-4 h-4 text-studio-gold" />
              <span>DSP Mastering Chain:</span>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-studio-text">
              <span className="px-2 py-0.5 rounded bg-studio-surface border border-studio-border">Warm EQ</span>
              <span className="px-2 py-0.5 rounded bg-studio-surface border border-studio-border">Mushaira Reverb</span>
              <span className="px-2 py-0.5 rounded bg-studio-surface border border-studio-border">Compressor</span>
            </div>
          </div>

          {/* Primary Action Button */}
          <button
            type="button"
            onClick={handleStartGeneration}
            className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-studio-gold via-studio-amber to-studio-gold hover:opacity-95 text-studio-bg font-bold text-base shadow-gold transition-all duration-200 flex items-center justify-center gap-2.5 cursor-pointer"
          >
            <Wand2 className="w-5 h-5" />
            <span>Generate Neural Voice-over</span>
            <span className="font-nastaliq text-lg font-bold pr-1">(آواز تیار کریں)</span>
          </button>
        </div>
      </div>

      {/* Progress & Live Terminal Modal */}
      <GenerationModal
        isOpen={isModalOpen}
        job={activeJob}
        logs={jobLogs}
        onCancel={handleCancelJob}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}

