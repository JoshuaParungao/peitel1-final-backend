Snack usage

1. Open https://snack.expo.dev/
2. Create a new snack and replace the default `App.js` with the contents of `mobile_app/snack/App.js`.
3. Update `API_BASE` at the top of the file to your Render API base, for example:
   `const API_BASE = 'https://your-app.onrender.com/api/';`
4. Add `axios` as a dependency in Snack (click "Add Dependency" and enter `axios`).
5. Run the snack. Use the web preview or scan the QR code with Expo Go.

Notes
- The Snack app uses token auth returned by `/api/auth/login/`. Make sure the staff account is approved in your Django admin (`/clinic/staff/approval/`).
- For local testing using Expo web, set API_BASE to your Render URL or `http://127.0.0.1:8000/api/` if backend runs locally.
- If you get CORS errors, add the Snack origin (shown in browser console) to `CORS_ALLOWED_ORIGINS` in your Django dev config.
