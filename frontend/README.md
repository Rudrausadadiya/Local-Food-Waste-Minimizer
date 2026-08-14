# Frontend — Local Food Waste Minimizer

React 18 single-page application built with Vite, Tailwind CSS, Framer Motion, and Zustand for state management.

---

## 🚀 Setup & Execution

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Configure Environment Variables**:
   ```bash
   cp .env.example .env.local
   ```
   Set `VITE_API_URL=http://localhost:8000/api/v1`.

4. **Start Development Server**:
   ```bash
   npm run dev
   ```
   Access the frontend application at `http://localhost:3000`.

5. **Build for Production**:
   ```bash
   npm run build
   ```

---

## ⚡ Performance Optimization & Bundle Chunking

`vite.config.js` configures Rollup `manualChunks` to isolate heavy, rarely-changing vendor libraries into separate cached chunks (`vendor-charts`, `vendor-maps`, `vendor-motion`), dropping the main entry chunk size by >50% (from 766 kB to ~355 kB).
