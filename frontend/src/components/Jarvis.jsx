import React from 'react';
import '../App.css'

const InteractiveSection = () => {
  return (
    <section id="Oval" className="mb-4 hidden">
      <div className="row">
        <div className="col-md-1"></div>
        <div className="col-md-10">
          <div className="d-flex justify-center items-center" style={{ height: '80vh' }}>
            {/* Canvas Element */}
            <canvas id="canvasOne" width="700" height="420" className="absolute"></canvas>

            {/* SVG Animation Wrapper */}
            <div id="JarvisHood" className="svg-frame">
              <div className="square relative w-100 h-100 flex justify-center items-center">
                <span className="circle span1"></span>
                <span className="circle span2"></span>
                <span className="circle span3"></span>
              </div>
            </div>
          </div>

          {/* Heading */}
          <h5 className="text-light text-center">Ask me anything</h5>

          {/* Input Field */}
          <div className="col-md-12 mt-4 pt-4">
            <div className="text-center">
              <div id="TextInput" className="d-flex bg-gray-800 border border-blue-500 rounded-lg shadow-lg p-1 mx-10">
                <input
                  type="text"
                  className="input-field bg-transparent border-none w-full outline-none text-white"
                  name="chatbox"
                  id="chatbox"
                  placeholder="Type here..."
                />
                {/* Buttons */}
                <button id="SendBtn" className="glow-on-hover hidden"><i className="bi bi-send"></i></button>
                <button id="MicBtn" className="glow-on-hover"><i className="bi bi-mic"></i></button>
                <button
                  id="ChatBtn"
                  className="glow-on-hover"
                  data-bs-toggle="offcanvas"
                  data-bs-target="#offcanvasScrolling"
                  aria-controls="offcanvasScrolling"
                >
                  <i className="bi bi-chat-dots"></i>
                </button>
                <button id="SettingsBtn" className="glow-on-hover"><i className="bi bi-gear"></i></button>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-1"></div>
      </div>
    </section>
  );
};

export default InteractiveSection;
