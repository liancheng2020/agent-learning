export const sampleDiff = `diff --git a/src/LoginButton.jsx b/src/LoginButton.jsx
--- a/src/LoginButton.jsx
+++ b/src/LoginButton.jsx
@@ -1,8 +1,13 @@
 export function LoginButton({ api }) {
+  const handleClick = async () => {
+    const result = await api.login();
+    localStorage.setItem("token", result.token);
+  };
+
   return (
-    <button onClick={() => api.login()}>
-      Login
+    <button onClick={handleClick}>
+      <img src="/login.svg" />
     </button>
   );
 }
`;

export const sampleCode = `export function LoginButton({ api }) {
  const handleClick = async () => {
    const result = await api.login();
    localStorage.setItem("token", result.token);
  };

  return (
    <button onClick={handleClick}>
      <img src="/login.svg" />
    </button>
  );
}
`;
