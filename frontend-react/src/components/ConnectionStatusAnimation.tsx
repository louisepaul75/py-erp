import React, { useEffect, useRef } from 'react';

interface ConnectionStatusAnimationProps {
  status: 'healthy' | 'warning' | 'error' | 'unknown';
  transactionCount?: number; // Number of PostgreSQL transactions
  transactionSpeed?: number; // Speed of PostgreSQL transactions (ms)
  className?: string;
}

const ConnectionStatusAnimation: React.FC<ConnectionStatusAnimationProps> = ({ 
  status, 
  transactionCount = 0,
  transactionSpeed = 0,
  className = '' 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Setting canvas dimensions
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Calculate density and speed based on transaction metrics
    const normalizedCount = Math.min(Math.max(transactionCount, 0), 1000);
    const normalizedSpeed = transactionSpeed > 0 ? Math.min(Math.max(1000 / transactionSpeed, 0.5), 10) : 1;
    
    // Define animation parameters based on status and transaction metrics
    const config = {
      healthy: {
        blockCount: Math.max(5, Math.floor(normalizedCount / 50)) || 15,
        speed: ((normalizedSpeed || 2) * 1.5) * 0.5, // Scaled down by half
        color: '#10b981' // green
      },
      warning: {
        blockCount: Math.max(3, Math.floor(normalizedCount / 100)) || 8,
        speed: ((normalizedSpeed || 1) * 1) * 0.5, // Scaled down by half
        color: '#f59e0b' // yellow
      },
      error: {
        blockCount: Math.max(2, Math.floor(normalizedCount / 200)) || 3,
        speed: ((normalizedSpeed || 0.5) * 0.5) * 0.5, // Scaled down by half
        color: '#ef4444' // red
      },
      unknown: {
        blockCount: 3,
        speed: 0.3 * 0.5, // Scaled down by half
        color: '#9ca3af' // gray
      }
    };
    
    const currentConfig = config[status] || config.unknown;
    
    // Create blocks
    const blocks = Array.from({ length: currentConfig.blockCount }, () => ({
      x: -20, // Start off-screen to the left
      y: 20 + Math.random() * (canvas.height - 40), // Random height within canvas
      width: 8 + Math.random() * 12, // Random width between 8-20px
      height: 4 + Math.random() * 6, // Random height between 4-10px
      speed: currentConfig.speed * (0.7 + Math.random() * 0.6), // Randomize speed slightly
      opacity: 0.7 + Math.random() * 0.3 // Random opacity
    }));
    
    // Animation loop
    let animationId: number;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw and move blocks
      blocks.forEach((block) => {
        // Move blocks from left to right
        block.x += block.speed;
        
        // Reset block position when it goes off-screen
        if (block.x > canvas.width) {
          block.x = -20;
          block.y = 20 + Math.random() * (canvas.height - 40);
          block.width = 8 + Math.random() * 12;
          block.height = 4 + Math.random() * 6;
        }
        
        // Draw block
        ctx.fillStyle = currentConfig.color;
        ctx.globalAlpha = block.opacity;
        ctx.beginPath();
        ctx.rect(block.x, block.y, block.width, block.height);
        ctx.fill();
      });
      
      // Draw a thin line across the middle as a "path"
      ctx.strokeStyle = currentConfig.color;
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.2;
      ctx.beginPath();
      ctx.moveTo(0, canvas.height / 2);
      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
      ctx.globalAlpha = 1;
      
      animationId = requestAnimationFrame(animate);
    };
    
    animate();
    
    // Clean up animation on unmount
    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [status, transactionCount, transactionSpeed]);
  
  return (
    <canvas 
      ref={canvasRef} 
      className={`w-full h-full rounded ${className}`}
    />
  );
};

export default ConnectionStatusAnimation; 