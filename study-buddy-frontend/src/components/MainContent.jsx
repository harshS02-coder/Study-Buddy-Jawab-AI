import FileUpload from "./FileUpload";
import ChatWindow from "./chatWindow";

function MainContent({ isFileUploaded, handleUploadSuccess, onUploadNewDocument, activeMode }) {

    return (
        <main className="content">
                {!isFileUploaded ? (
                  <div className="grid">
                    <section className="glass-card upload-card">
                      <h2 className="section-title">Get Started</h2>
                      <p className="section-help">Drop a PDF or click to select</p>
                      <FileUpload onUploadSuccess={handleUploadSuccess} activeMode={activeMode} />
                      <div className="feature-badges">
                        <span className="badge">PDF</span>
                        <span className="badge">Fast RAG</span>
                        <span className="badge">Sources</span>
                      </div>
                    </section>
        
                    <aside className="glass-card info-card">
                      <h3 className="info-title">What you can do</h3>
                      <ul className="info-list">
                        <li>Summarize chapters and key concepts</li>
                        <li>Ask targeted questions about any section</li>
                        <li>See cited source snippets for each answer</li>
                      </ul>
                      <div className="tip">
                        Pro tip: Ask specific questions like “Explain theorem 2.3 with an example”.
                      </div>
                    </aside>
                  </div>
                ) : (
                  <section className="glass-card chat-card">
                    <div className="chat-header">
                      <div className="chat-header-left">
                        <h2 className="section-title">Your Q&A Session</h2>
                        <p className="section-help">Ask anything from the uploaded document</p>
                      </div>

                      <button
                        className="upload-new-btn"
                        onClick={() => {
                          if (typeof onUploadNewDocument === "function") {
                            onUploadNewDocument();
                          }
                        }}
                      >
                        Upload New Document
                      </button>
                    </div>
                    <ChatWindow activeMode={activeMode}/>
                  </section>
                )}
              </main>
    );
}

export default MainContent;