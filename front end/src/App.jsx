function App() {
 const [professorId, setProfessorId] = useState("");
 const [canvasCourseId, setCanvasCourseId] = useState("");
 const [syllabus, setSyllabus] = useState("");
 const [prediction, setPrediction] = useState(null);
 const [loading, setLoading] = useState(false);


 const handleFinalPrediction = async (e) => {
   e.preventDefault();
   setLoading(true);
   setPrediction(null); // hide results while loading


   try {
     const payload = {
       syllabus_text: syllabus,
       professor_id: professorId ? parseInt(professorId) : null,
       canvas_course_id: canvasCourseId ? parseInt(canvasCourseId) : null,
     };


     const res = await axios.post(
       "http://127.0.0.1:8000/api/predict-grade/",
       payload
     );
     setPrediction(res.data);
   } catch (err) {
     console.error("Prediction error:", err.response?.data || err.message);
   } finally {
     setLoading(false);
   }
 };


 const formatNumber = (num) => {
   if (num === null || num === undefined || isNaN(num)) return "N/A";
   return Math.round(num * 10) / 10;
 };


 // Stable grade animation: only restarts when final_score changes
 const animatedGrade = useStableGradeCountUp(prediction?.final_score ?? 0, 2000);


 return (
   <div className="app-container">
     <h1 className="app-title">iGradeU</h1>


     {/* Form */}
     <form className="prediction-form-inline" onSubmit={handleFinalPrediction}>
       <input
         type="text"
         value={professorId}
         onChange={(e) => setProfessorId(e.target.value)}
         placeholder="Professor ID"
         required
       />
       <input
         type="text"
         value={canvasCourseId}
         onChange={(e) => setCanvasCourseId(e.target.value)}
         placeholder="Canvas Course ID"
         required
       />
       <input
         type="text"
         value={syllabus}
         onChange={(e) => setSyllabus(e.target.value)}
         placeholder="Paste syllabus here..."
         required
       />
       <button type="submit" disabled={loading}>
         {loading ? "⏳" : "🔮"}
       </button>
     </form>


     {(prediction || loading) && (
       <div className="results">
         <h2 className="fade-in" style={{ animationDelay: "0s" }}>
           📊 Prediction Results
         </h2>


         {/* 🔹 Grade OR Loader */}
         <div
           className="score-highlight fade-in"
           style={{ animationDelay: "0.5s" }}
         >
           {loading ? (
             <div className="loader">
               <div className="dot-square">
                 <div></div><div></div><div></div><div></div>
               </div>
             </div>
           ) : (
             `${animatedGrade}%`
           )}
         </div>


         {!loading && prediction && (
           <>
             {/* 🔹 Margin + Range */}
             <div
               className="metrics-inline fade-in"
               style={{ animationDelay: "1s" }}
             >
               <div className="gradient-text">
                 <b>Margin of Error:</b> ±{prediction.margin_of_error ?? "N/A"}
               </div>
               <div className="gradient-text">
                 <b>Range:</b>{" "}
                 {Array.isArray(prediction.range)
                   ? `${formatNumber(prediction.range[0])} – ${formatNumber(
                       prediction.range[1]
                     )}`
                   : "N/A"}
               </div>
             </div>


             {/* 🔹 Strength Metrics */}
             <div className="fade-in" style={{ animationDelay: "1.5s" }}>
               <h3> Your Strength Score</h3>
               <div className="strengths">
                 <StrengthBar
                   label="Overall Strength"
                   value={prediction.overall_strength}
                   delay={0}
                 />
                 <StrengthBar
                   label="Punctual Strength"
                   value={prediction.punctual_strength}
                   delay={400}
                 />
               </div>
             </div>


             {/* 🔹 Category Strengths */}
             <div className="fade-in" style={{ animationDelay: "2s" }}>
               <h3>Your Category Strength Score</h3>
               <div className="strengths">
                 {Object.entries(prediction.category_strengths || {}).map(
                   ([key, value], idx) => (
                     <StrengthBar
                       key={key}
                       label={key}
                       value={value}
                       delay={idx * 400}
                     />
                   )
                 )}
               </div>
             </div>


             {/* 🔹 Course Weights */}
             <div className="fade-in" style={{ animationDelay: "2.5s" }}>
               <h3>
                 {prediction.course_name
                   ? `${prediction.course_name} Weight Score`
                   : "Course Weights"}
               </h3>


               <div className="strengths">
                 {[
                   { label: "Projects", value: prediction.projects },
                   { label: "Assignments", value: prediction.assignments },
                   { label: "Exams", value: prediction.exams },
                   { label: "Participation", value: prediction.participation },
                 ].map(({ label, value }, idx) => (
                   <StrengthBar
                     key={label}
                     label={label}
                     value={value}
                     delay={idx * 400}
                   />
                 ))}
               </div>
             </div>


             {/* 🔹 Professor Difficulty */}
             {prediction.rmp && (
               <div className="fade-in" style={{ animationDelay: "3s" }}>
                 <h3>Class Difficulty Scores</h3>
                 <div className="strengths">
                   <StrengthBar
                     label="Difficulty"
                     value={prediction.rmp.avg_difficulty}
                     max={5}
                     delay={0}
                   />
                   <StrengthBar
                     label="Would Take Again"
                     value={prediction.rmp.would_take_again_percent}
                     delay={400}
                   />
                 </div>
               </div>
             )}


             {/* 🔹 AI Advice */}
             {prediction.advice && (
               <div
                 className="advice-section fade-in"
                 style={{ animationDelay: "3.5s" }}
               >
                 <h3>Verdict</h3>


                 {[
                   "Areas You Will Do Well At:",
                   "Areas You May Struggle With:",
                   "Final Verdict:",
                 ].map((label, idx) => {
                   const regex = new RegExp(
                     `${label}[\\s\\S]*?(?=(Areas You May Struggle With:|Final Verdict:|$))`,
                     "i"
                   );
                   const match = prediction.advice.match(regex);


                   return (
                     <div
                       key={idx}
                       className="advice-card"
                       style={{ animationDelay: `${(idx + 1) * 0.3}s` }}
                     >
                       <span className="advice-label">{label}</span>
                       <p>
                         {match ? match[0].replace(label, "").trim() : "N/A"}
                       </p>
                     </div>
                   );
                 })}
               </div>
             )}
           </>
         )}
       </div>
     )}
   </div>
 );
}


export default App;

