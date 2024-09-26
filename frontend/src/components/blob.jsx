import { useEffect, useRef, useState, useMemo } from 'react';
import './Jarvis.css';
import PropTypes from 'prop-types';

const Jarvis = ({ isRecording, isMinimized, isClosing, playerRef }) => {
  const canvasRef = useRef(null);
  const [position, setPosition] = useState({ top: '50%', left: '50%' });

  Jarvis.propTypes = {
    isRecording: PropTypes.bool.isRequired,
    isMinimized: PropTypes.bool.isRequired,
    isClosing: PropTypes.bool.isRequired,
    playerRef: PropTypes.object.isRequired
  };

  const particleConfig = useMemo(() => ({
    count: 1000,
    size: 2,
    maxSpeed: 0.1,
    minSpeed: 0.02,
    color: isRecording ? [235, 94, 52] : [0, 72, 255],
    blurFactor: 0.5,
  }), [isRecording]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    let sphereRad = 100;
    let radius_sp = 0.9;

    let displayWidth;
    let displayHeight;
    let timer;
    let wait;
    let count;
    let numToAddEachFrame;
    let particleList;
    let recycleBin;
    let particleAlpha;
    let r, g, b;
    let fLen;
    let m;
    let projCenterX;
    let projCenterY;
    let zMax;
    let turnAngle;
    let turnSpeed;
    let sphereCenterX, sphereCenterY, sphereCenterZ;
    let particleRad;
    let zeroAlphaDepth;
    let randAccelX, randAccelY, randAccelZ;
    let gravity;
    let rgbString;

    function init() {
      wait = 1;
      count = wait - 1;
      numToAddEachFrame = 8;

      if(isRecording){
        r = 235;
        g = 94;
        b = 52;
      } else {
        r = 0;
        g = 72;
        b = 255;
      }   

      rgbString = "rgba(" + r + "," + g + "," + b + ",";
      particleAlpha = 1;

      displayWidth = canvas.width;
      displayHeight = canvas.height;

      fLen = 320;
      projCenterX = displayWidth / 2;
      projCenterY = displayHeight / 2;

      zMax = fLen - 2;

      particleList = {};
      recycleBin = {};

      randAccelX = 0.1;
      randAccelY = 0.1;
      randAccelZ = 0.1;

      gravity = 0;

      particleRad = 1.8;

      sphereCenterX = displayWidth / 2;
      sphereCenterY = displayHeight / 2;
      sphereCenterZ = -3 - sphereRad;

      zeroAlphaDepth = -750;

      turnSpeed = 2 * Math.PI / 1200;
      turnAngle = 0;

      timer = setInterval(onTimer, 10 / 24);
    }

    function onTimer() {
      count++;
      if (count >= wait) {
        count = 0;
        for (let i = 0; i < numToAddEachFrame; i++) {
          let theta = Math.random() * 2 * Math.PI;
          let phi = Math.acos(Math.random() * 2 - 1);
          let x0 = sphereRad * Math.sin(phi) * Math.cos(theta);
          let y0 = sphereRad * Math.sin(phi) * Math.sin(theta);
          let z0 = sphereRad * Math.cos(phi);

          let p = addParticle(x0, y0, z0, 0, 0, 0);

          p.attack = 50;
          p.hold = 50;
          p.decay = 100;
          p.initValue = 0;
          p.holdValue = particleAlpha;
          p.lastValue = 0;

          p.stuckTime = 90 + Math.random() * 20;

          p.accelX = 0;
          p.accelY = gravity;
          p.accelZ = 0;
        }
      }

      turnAngle = (turnAngle + turnSpeed) % (2 * Math.PI);
      let sinAngle = Math.sin(turnAngle);
      let cosAngle = Math.cos(turnAngle);

      context.clearRect(0, 0, displayWidth, displayHeight);

      let p = particleList.first;
      while (p != null) {
        let nextParticle = p.next;

        p.age++;

        if (p.age > p.stuckTime) {
          p.velX += p.accelX + randAccelX * (Math.random() * 2 - 1);
          p.velY += p.accelY + randAccelY * (Math.random() * 2 - 1);
          p.velZ += p.accelZ + randAccelZ * (Math.random() * 2 - 1);

          p.x += p.velX;
          p.y += p.velY;
          p.z += p.velZ;
        }

        let rotX = cosAngle * p.x + sinAngle * p.z;
        let rotZ = -sinAngle * p.x + cosAngle * p.z;
        
        m = radius_sp * fLen / (fLen - rotZ);
        p.projX = rotX * m + projCenterX;
        p.projY = p.y * m + projCenterY;

        if (p.age < p.attack + p.hold + p.decay) {
          if (p.age < p.attack) {
            p.alpha = (p.holdValue - p.initValue) / p.attack * p.age + p.initValue;
          } else if (p.age < p.attack + p.hold) {
            p.alpha = p.holdValue;
          } else if (p.age < p.attack + p.hold + p.decay) {
            p.alpha = (p.lastValue - p.holdValue) / p.decay * (p.age - p.attack - p.hold) + p.holdValue;
          }
        } else {
          p.dead = true;
        }

        if ((p.projX > displayWidth) || (p.projX < 0) || (p.projY < 0) || (p.projY > displayHeight) || (rotZ > zMax)) {
          recycle(p);
        } else {
          let depthAlphaFactor = (1 - rotZ / zeroAlphaDepth);
          depthAlphaFactor = (depthAlphaFactor > 1) ? 1 : ((depthAlphaFactor < 0) ? 0 : depthAlphaFactor);
          context.fillStyle = rgbString + depthAlphaFactor * p.alpha + ")";

          context.beginPath();
          context.arc(p.projX, p.projY, m * particleRad, 0, 2 * Math.PI, false);
          context.closePath();
          context.fill();
        }

        p = nextParticle;
      }
    }

    function addParticle(x0, y0, z0, vx0, vy0, vz0) {
      let newParticle;

      if (recycleBin.first != null) {
        newParticle = recycleBin.first;
        if (newParticle.next != null) {
          recycleBin.first = newParticle.next;
          newParticle.next.prev = null;
        } else {
          recycleBin.first = null;
        }
      } else {
        newParticle = {};
      }

      if (particleList.first == null) {
        particleList.first = newParticle;
        newParticle.prev = null;
        newParticle.next = null;
      } else {
        newParticle.next = particleList.first;
        particleList.first.prev = newParticle;
        particleList.first = newParticle;
        newParticle.prev = null;
      }

      newParticle.x = x0;
      newParticle.y = y0;
      newParticle.z = z0;
      newParticle.velX = vx0;
      newParticle.velY = vy0;
      newParticle.velZ = vz0;
      newParticle.age = 0;
      newParticle.dead = false;
      return newParticle;
    }

    function recycle(p) {
      if (particleList.first == p) {
        if (p.next != null) {
          p.next.prev = null;
          particleList.first = p.next;
        } else {
          particleList.first = null;
        }
      } else {
        if (p.next == null) {
          p.prev.next = null;
        } else {
          p.prev.next = p.next;
          p.next.prev = p.prev;
        }
      }
      if (recycleBin.first == null) {
        recycleBin.first = p;
        p.prev = null;
        p.next = null;
      } else {
        p.next = recycleBin.first;
        recycleBin.first.prev = p;
        recycleBin.first = p;
        p.prev = null;
      }
    }

    init();

    return () => {
      clearInterval(timer);
    };
  }, [isRecording]);

  useEffect(() => {
    if (isMinimized && playerRef.current && !isClosing) {
      const rect = playerRef.current.getBoundingClientRect();
      setPosition({
        top: `${rect.top}px`,
        left: `${rect.left - 130}px`, // Adjust this value as needed
      });
    } else {
      setPosition({ top: '50%', left: '50%' });
    }
  }, [isMinimized, isClosing, playerRef]);

  return (
    <div id="JarvisHood" className={isMinimized && !isClosing ? 'minimized' : ''} style={{
      width: '400px', 
      height: '400px', 
      position: 'fixed',
      transition: 'all 0.5s ease-in-out',
      top: isMinimized && !isClosing ? position.top : '50%',
      left: isMinimized && !isClosing ? position.left : '50%',
      transform: isMinimized && !isClosing
        ? 'scale(0.25)' 
        : 'translate(-50%, -50%) scale(1)',
      transformOrigin: 'top left',
      zIndex: isMinimized ? 1001 : 1
    }}>
      <canvas ref={canvasRef} width="400" height="400" style={{
        position: 'absolute',
        zIndex: 1,
        top: '0',
        left: '0',
        width: '100%',
        height: '100%'
      }}></canvas>
      <div className={`square ${isRecording ? 'recording' : ''}`}>
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
};

export default Jarvis;