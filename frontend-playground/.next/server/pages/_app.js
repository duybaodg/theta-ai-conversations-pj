/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(() => {
var exports = {};
exports.id = "pages/_app";
exports.ids = ["pages/_app"];
exports.modules = {

/***/ "./src/cloud/useCloud.tsx":
/*!********************************!*\
  !*** ./src/cloud/useCloud.tsx ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   CloudProvider: () => (/* binding */ CloudProvider),\n/* harmony export */   useCloud: () => (/* binding */ useCloud)\n/* harmony export */ });\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-dev-runtime */ \"react/jsx-dev-runtime\");\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__);\n\nfunction CloudProvider({ children }) {\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.Fragment, {\n        children: children\n    }, void 0, false);\n}\nfunction useCloud() {\n    const generateToken = async ()=>{\n        throw new Error(\"Not implemented\");\n    };\n    const wsUrl = \"\";\n    return {\n        generateToken,\n        wsUrl\n    };\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY2xvdWQvdXNlQ2xvdWQudHN4IiwibWFwcGluZ3MiOiI7Ozs7Ozs7O0FBQU8sU0FBU0EsY0FBYyxFQUFFQyxRQUFRLEVBQWlDO0lBQ3ZFLHFCQUFPO2tCQUFHQTs7QUFDWjtBQUVPLFNBQVNDO0lBQ2QsTUFBTUMsZ0JBQXVDO1FBQzNDLE1BQU0sSUFBSUMsTUFBTTtJQUNsQjtJQUNBLE1BQU1DLFFBQVE7SUFFZCxPQUFPO1FBQUVGO1FBQWVFO0lBQU07QUFDaEMiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9hZ2VudHMtcGxheWdyb3VuZC8uL3NyYy9jbG91ZC91c2VDbG91ZC50c3g/MzNiNCJdLCJzb3VyY2VzQ29udGVudCI6WyJleHBvcnQgZnVuY3Rpb24gQ2xvdWRQcm92aWRlcih7IGNoaWxkcmVuIH06IHsgY2hpbGRyZW46IFJlYWN0LlJlYWN0Tm9kZSB9KSB7XHJcbiAgcmV0dXJuIDw+e2NoaWxkcmVufTwvPjtcclxufVxyXG5cclxuZXhwb3J0IGZ1bmN0aW9uIHVzZUNsb3VkKCkge1xyXG4gIGNvbnN0IGdlbmVyYXRlVG9rZW46ICgpID0+IFByb21pc2U8c3RyaW5nPiA9IGFzeW5jICgpID0+IHtcclxuICAgIHRocm93IG5ldyBFcnJvcihcIk5vdCBpbXBsZW1lbnRlZFwiKTtcclxuICB9O1xyXG4gIGNvbnN0IHdzVXJsID0gXCJcIjtcclxuXHJcbiAgcmV0dXJuIHsgZ2VuZXJhdGVUb2tlbiwgd3NVcmwgfTtcclxufSJdLCJuYW1lcyI6WyJDbG91ZFByb3ZpZGVyIiwiY2hpbGRyZW4iLCJ1c2VDbG91ZCIsImdlbmVyYXRlVG9rZW4iLCJFcnJvciIsIndzVXJsIl0sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/cloud/useCloud.tsx\n");

/***/ }),

/***/ "./src/pages/_app.tsx":
/*!****************************!*\
  !*** ./src/pages/_app.tsx ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ App)\n/* harmony export */ });\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-dev-runtime */ \"react/jsx-dev-runtime\");\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _cloud_useCloud__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @/cloud/useCloud */ \"./src/cloud/useCloud.tsx\");\n/* harmony import */ var _livekit_components_styles_components_participant__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @livekit/components-styles/components/participant */ \"./node_modules/.pnpm/@livekit+components-styles@1.1.4/node_modules/@livekit/components-styles/dist/general/components/participant/index.css\");\n/* harmony import */ var _livekit_components_styles_components_participant__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_livekit_components_styles_components_participant__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var _styles_globals_css__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @/styles/globals.css */ \"./src/styles/globals.css\");\n/* harmony import */ var _styles_globals_css__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_styles_globals_css__WEBPACK_IMPORTED_MODULE_3__);\n\n\n\n\nfunction App({ Component, pageProps }) {\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(_cloud_useCloud__WEBPACK_IMPORTED_MODULE_1__.CloudProvider, {\n        children: /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(Component, {\n            ...pageProps\n        }, void 0, false, {\n            fileName: \"C:\\\\Users\\\\janpa\\\\OneDrive\\\\Desktop\\\\AI LiveKit - New Frontend\\\\theta-ai-conversations-pj\\\\frontend-playground\\\\src\\\\pages\\\\_app.tsx\",\n            lineNumber: 9,\n            columnNumber: 7\n        }, this)\n    }, void 0, false, {\n        fileName: \"C:\\\\Users\\\\janpa\\\\OneDrive\\\\Desktop\\\\AI LiveKit - New Frontend\\\\theta-ai-conversations-pj\\\\frontend-playground\\\\src\\\\pages\\\\_app.tsx\",\n        lineNumber: 8,\n        columnNumber: 5\n    }, this);\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvcGFnZXMvX2FwcC50c3giLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7Ozs7O0FBQWlEO0FBQ1U7QUFDN0I7QUFHZixTQUFTQyxJQUFJLEVBQUVDLFNBQVMsRUFBRUMsU0FBUyxFQUFZO0lBQzVELHFCQUNFLDhEQUFDSCwwREFBYUE7a0JBQ1osNEVBQUNFO1lBQVcsR0FBR0MsU0FBUzs7Ozs7Ozs7Ozs7QUFHOUIiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9hZ2VudHMtcGxheWdyb3VuZC8uL3NyYy9wYWdlcy9fYXBwLnRzeD9mOWQ2Il0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IENsb3VkUHJvdmlkZXIgfSBmcm9tIFwiQC9jbG91ZC91c2VDbG91ZFwiO1xyXG5pbXBvcnQgXCJAbGl2ZWtpdC9jb21wb25lbnRzLXN0eWxlcy9jb21wb25lbnRzL3BhcnRpY2lwYW50XCI7XHJcbmltcG9ydCBcIkAvc3R5bGVzL2dsb2JhbHMuY3NzXCI7XHJcbmltcG9ydCB0eXBlIHsgQXBwUHJvcHMgfSBmcm9tIFwibmV4dC9hcHBcIjtcclxuXHJcbmV4cG9ydCBkZWZhdWx0IGZ1bmN0aW9uIEFwcCh7IENvbXBvbmVudCwgcGFnZVByb3BzIH06IEFwcFByb3BzKSB7XHJcbiAgcmV0dXJuIChcclxuICAgIDxDbG91ZFByb3ZpZGVyPlxyXG4gICAgICA8Q29tcG9uZW50IHsuLi5wYWdlUHJvcHN9IC8+XHJcbiAgICA8L0Nsb3VkUHJvdmlkZXI+XHJcbiAgKTtcclxufVxyXG4iXSwibmFtZXMiOlsiQ2xvdWRQcm92aWRlciIsIkFwcCIsIkNvbXBvbmVudCIsInBhZ2VQcm9wcyJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/pages/_app.tsx\n");

/***/ }),

/***/ "./src/styles/globals.css":
/*!********************************!*\
  !*** ./src/styles/globals.css ***!
  \********************************/
/***/ (() => {



/***/ }),

/***/ "react/jsx-dev-runtime":
/*!****************************************!*\
  !*** external "react/jsx-dev-runtime" ***!
  \****************************************/
/***/ ((module) => {

"use strict";
module.exports = require("react/jsx-dev-runtime");

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = __webpack_require__.X(0, ["vendor-chunks/@livekit+components-styles@1.1.4"], () => (__webpack_exec__("./src/pages/_app.tsx")));
module.exports = __webpack_exports__;

})();