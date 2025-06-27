"use strict";
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
exports.id = "pages/_document";
exports.ids = ["pages/_document"];
exports.modules = {

/***/ "./pages/_document.tsx":
/*!*****************************!*\
  !*** ./pages/_document.tsx ***!
  \*****************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {\n__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (__WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ \"react\");\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var next_document__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! next/document */ \"./node_modules/next/document.js\");\n/* harmony import */ var next_document__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(next_document__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var _chakra_ui_react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @chakra-ui/react */ \"@chakra-ui/react\");\n/* harmony import */ var _theme__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../theme */ \"./theme.tsx\");\nvar __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([_chakra_ui_react__WEBPACK_IMPORTED_MODULE_2__, _theme__WEBPACK_IMPORTED_MODULE_3__]);\n([_chakra_ui_react__WEBPACK_IMPORTED_MODULE_2__, _theme__WEBPACK_IMPORTED_MODULE_3__] = __webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__);\nfunction _typeof(o) { \"@babel/helpers - typeof\"; return _typeof = \"function\" == typeof Symbol && \"symbol\" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && \"function\" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? \"symbol\" : typeof o; }, _typeof(o); }\nfunction _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError(\"Cannot call a class as a function\"); } }\nfunction _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if (\"value\" in descriptor) descriptor.writable = true; Object.defineProperty(target, _toPropertyKey(descriptor.key), descriptor); } }\nfunction _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, \"prototype\", { writable: false }); return Constructor; }\nfunction _toPropertyKey(arg) { var key = _toPrimitive(arg, \"string\"); return _typeof(key) === \"symbol\" ? key : String(key); }\nfunction _toPrimitive(input, hint) { if (_typeof(input) !== \"object\" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || \"default\"); if (_typeof(res) !== \"object\") return res; throw new TypeError(\"@@toPrimitive must return a primitive value.\"); } return (hint === \"string\" ? String : Number)(input); }\nfunction _callSuper(_this, derived, args) {\n  function isNativeReflectConstruct() {\n    if (typeof Reflect === \"undefined\" || !Reflect.construct) return false;\n    if (Reflect.construct.sham) return false;\n    if (typeof Proxy === \"function\") return true;\n    try {\n      return !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {}));\n    } catch (e) {\n      return false;\n    }\n  }\n  derived = _getPrototypeOf(derived);\n  return _possibleConstructorReturn(_this, isNativeReflectConstruct() ? Reflect.construct(derived, args || [], _getPrototypeOf(_this).constructor) : derived.apply(_this, args));\n}\nfunction _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === \"object\" || typeof call === \"function\")) { return call; } else if (call !== void 0) { throw new TypeError(\"Derived constructors may only return object or undefined\"); } return _assertThisInitialized(self); }\nfunction _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError(\"this hasn't been initialised - super() hasn't been called\"); } return self; }\nfunction _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }\nfunction _inherits(subClass, superClass) { if (typeof superClass !== \"function\" && superClass !== null) { throw new TypeError(\"Super expression must either be null or a function\"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, \"prototype\", { writable: false }); if (superClass) _setPrototypeOf(subClass, superClass); }\nfunction _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }\n// frontend/pages/_document.tsx\n\n\n\n\nvar MyDocument = /*#__PURE__*/function (_Document) {\n  function MyDocument() {\n    _classCallCheck(this, MyDocument);\n    return _callSuper(this, MyDocument, arguments);\n  }\n  _inherits(MyDocument, _Document);\n  return _createClass(MyDocument, [{\n    key: \"render\",\n    value: function render() {\n      return /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(next_document__WEBPACK_IMPORTED_MODULE_1__.Html, {\n        lang: \"en\"\n      }, /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(next_document__WEBPACK_IMPORTED_MODULE_1__.Head, null), /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(\"body\", null, /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_chakra_ui_react__WEBPACK_IMPORTED_MODULE_2__.ColorModeScript, {\n        initialColorMode: _theme__WEBPACK_IMPORTED_MODULE_3__[\"default\"].config.initialColorMode\n      }), /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(next_document__WEBPACK_IMPORTED_MODULE_1__.Main, null), /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(next_document__WEBPACK_IMPORTED_MODULE_1__.NextScript, null)));\n    }\n  }]);\n}((next_document__WEBPACK_IMPORTED_MODULE_1___default()));\n/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (MyDocument);\n__webpack_async_result__();\n} catch(e) { __webpack_async_result__(e); } });//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9wYWdlcy9fZG9jdW1lbnQudHN4IiwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FBQUE7QUFDeUI7QUFDNkM7QUFDcEI7QUFDdEI7QUFBQSxJQUV0QlEsVUFBVSwwQkFBQUMsU0FBQTtFQUFBLFNBQUFELFdBQUE7SUFBQUUsZUFBQSxPQUFBRixVQUFBO0lBQUEsT0FBQUcsVUFBQSxPQUFBSCxVQUFBLEVBQUFJLFNBQUE7RUFBQTtFQUFBQyxTQUFBLENBQUFMLFVBQUEsRUFBQUMsU0FBQTtFQUFBLE9BQUFLLFlBQUEsQ0FBQU4sVUFBQTtJQUFBTyxHQUFBO0lBQUFDLEtBQUEsRUFDZCxTQUFBQyxNQUFNQSxDQUFBLEVBQUc7TUFDUCxvQkFDRWpCLDBEQUFBLENBQUNFLCtDQUFJO1FBQUNpQixJQUFJLEVBQUM7TUFBSSxnQkFDYm5CLDBEQUFBLENBQUNHLCtDQUFJLE1BQUUsQ0FBQyxlQUNSSCwwREFBQSw0QkFFRUEsMERBQUEsQ0FBQ00sNkRBQWU7UUFBQ2MsZ0JBQWdCLEVBQUViLHFEQUFZLENBQUNhO01BQWlCLENBQUUsQ0FBQyxlQUNwRXBCLDBEQUFBLENBQUNJLCtDQUFJLE1BQUUsQ0FBQyxlQUNSSiwwREFBQSxDQUFDSyxxREFBVSxNQUFFLENBQ1QsQ0FDRixDQUFDO0lBRVg7RUFBQztBQUFBLEVBYnNCSixzREFBUTtBQWdCakMsaUVBQWVPLFVBQVUsRSIsInNvdXJjZXMiOlsid2VicGFjazovL3JlY2FsbGd1YXJkLWZyb250ZW5kLy4vcGFnZXMvX2RvY3VtZW50LnRzeD9kMzdkIl0sInNvdXJjZXNDb250ZW50IjpbIi8vIGZyb250ZW5kL3BhZ2VzL19kb2N1bWVudC50c3hcclxuaW1wb3J0IFJlYWN0IGZyb20gJ3JlYWN0J1xyXG5pbXBvcnQgRG9jdW1lbnQsIHsgSHRtbCwgSGVhZCwgTWFpbiwgTmV4dFNjcmlwdCB9IGZyb20gJ25leHQvZG9jdW1lbnQnXHJcbmltcG9ydCB7IENvbG9yTW9kZVNjcmlwdCB9IGZyb20gJ0BjaGFrcmEtdWkvcmVhY3QnXHJcbmltcG9ydCB0aGVtZSBmcm9tICcuLi90aGVtZSdcclxuXHJcbmNsYXNzIE15RG9jdW1lbnQgZXh0ZW5kcyBEb2N1bWVudCB7XHJcbiAgcmVuZGVyKCkge1xyXG4gICAgcmV0dXJuIChcclxuICAgICAgPEh0bWwgbGFuZz1cImVuXCI+XHJcbiAgICAgICAgPEhlYWQgLz5cclxuICAgICAgICA8Ym9keT5cclxuICAgICAgICAgIHsvKiBlbnN1cmVzIENoYWtyYSdzIGluaXRpYWwgY29sb3IgbW9kZSBpcyByZXNwZWN0ZWQgb24gZmlyc3QgcGFpbnQgKi99XHJcbiAgICAgICAgICA8Q29sb3JNb2RlU2NyaXB0IGluaXRpYWxDb2xvck1vZGU9e3RoZW1lLmNvbmZpZy5pbml0aWFsQ29sb3JNb2RlfSAvPlxyXG4gICAgICAgICAgPE1haW4gLz5cclxuICAgICAgICAgIDxOZXh0U2NyaXB0IC8+XHJcbiAgICAgICAgPC9ib2R5PlxyXG4gICAgICA8L0h0bWw+XHJcbiAgICApXHJcbiAgfVxyXG59XHJcblxyXG5leHBvcnQgZGVmYXVsdCBNeURvY3VtZW50XHJcbiJdLCJuYW1lcyI6WyJSZWFjdCIsIkRvY3VtZW50IiwiSHRtbCIsIkhlYWQiLCJNYWluIiwiTmV4dFNjcmlwdCIsIkNvbG9yTW9kZVNjcmlwdCIsInRoZW1lIiwiTXlEb2N1bWVudCIsIl9Eb2N1bWVudCIsIl9jbGFzc0NhbGxDaGVjayIsIl9jYWxsU3VwZXIiLCJhcmd1bWVudHMiLCJfaW5oZXJpdHMiLCJfY3JlYXRlQ2xhc3MiLCJrZXkiLCJ2YWx1ZSIsInJlbmRlciIsImNyZWF0ZUVsZW1lbnQiLCJsYW5nIiwiaW5pdGlhbENvbG9yTW9kZSIsImNvbmZpZyJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./pages/_document.tsx\n");

/***/ }),

/***/ "./theme.tsx":
/*!*******************!*\
  !*** ./theme.tsx ***!
  \*******************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {\n__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (__WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/* harmony import */ var _chakra_ui_react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @chakra-ui/react */ \"@chakra-ui/react\");\nvar __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([_chakra_ui_react__WEBPACK_IMPORTED_MODULE_0__]);\n_chakra_ui_react__WEBPACK_IMPORTED_MODULE_0__ = (__webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__)[0];\n\nvar theme = (0,_chakra_ui_react__WEBPACK_IMPORTED_MODULE_0__.extendTheme)({\n  fonts: {\n    heading: \"'Inter', system-ui, sans-serif\",\n    body: \"'Inter', system-ui, sans-serif\"\n  },\n  colors: {\n    brand: {\n      50: '#f5faff',\n      100: '#e0f2ff',\n      500: '#1e88e5',\n      700: '#1565c0'\n    }\n  },\n  fontWeights: {\n    normal: 400,\n    medium: 600,\n    bold: 700\n  },\n  components: {\n    Button: {\n      baseStyle: {\n        borderRadius: 'md'\n      }\n    },\n    Table: {\n      baseStyle: {\n        th: {\n          fontWeight: 'medium'\n        }\n      }\n    }\n  }\n});\n/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (theme);\n__webpack_async_result__();\n} catch(e) { __webpack_async_result__(e); } });//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi90aGVtZS50c3giLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7QUFBK0M7QUFFL0MsSUFBTUMsS0FBSyxHQUFHRCw2REFBVyxDQUFDO0VBQ3hCRSxLQUFLLEVBQUU7SUFDTEMsT0FBTyxrQ0FBa0M7SUFDekNDLElBQUk7RUFDTixDQUFDO0VBQ0RDLE1BQU0sRUFBRTtJQUNOQyxLQUFLLEVBQUU7TUFDTCxFQUFFLEVBQUUsU0FBUztNQUNiLEdBQUcsRUFBRSxTQUFTO01BQ2QsR0FBRyxFQUFFLFNBQVM7TUFDZCxHQUFHLEVBQUU7SUFDUDtFQUNGLENBQUM7RUFDREMsV0FBVyxFQUFFO0lBQ1hDLE1BQU0sRUFBRSxHQUFHO0lBQ1hDLE1BQU0sRUFBRSxHQUFHO0lBQ1hDLElBQUksRUFBRTtFQUNSLENBQUM7RUFDREMsVUFBVSxFQUFFO0lBQ1ZDLE1BQU0sRUFBRTtNQUNOQyxTQUFTLEVBQUU7UUFBRUMsWUFBWSxFQUFFO01BQUs7SUFDbEMsQ0FBQztJQUNEQyxLQUFLLEVBQUU7TUFDTEYsU0FBUyxFQUFFO1FBQ1RHLEVBQUUsRUFBRTtVQUFFQyxVQUFVLEVBQUU7UUFBUztNQUM3QjtJQUNGO0VBQ0Y7QUFDRixDQUFDLENBQUM7QUFFRixpRUFBZWhCLEtBQUssRSIsInNvdXJjZXMiOlsid2VicGFjazovL3JlY2FsbGd1YXJkLWZyb250ZW5kLy4vdGhlbWUudHN4P2VhODEiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgZXh0ZW5kVGhlbWUgfSBmcm9tICdAY2hha3JhLXVpL3JlYWN0JztcclxuXHJcbmNvbnN0IHRoZW1lID0gZXh0ZW5kVGhlbWUoe1xyXG4gIGZvbnRzOiB7XHJcbiAgICBoZWFkaW5nOiBgJ0ludGVyJywgc3lzdGVtLXVpLCBzYW5zLXNlcmlmYCxcclxuICAgIGJvZHk6IGAnSW50ZXInLCBzeXN0ZW0tdWksIHNhbnMtc2VyaWZgLFxyXG4gIH0sXHJcbiAgY29sb3JzOiB7XHJcbiAgICBicmFuZDoge1xyXG4gICAgICA1MDogJyNmNWZhZmYnLFxyXG4gICAgICAxMDA6ICcjZTBmMmZmJyxcclxuICAgICAgNTAwOiAnIzFlODhlNScsXHJcbiAgICAgIDcwMDogJyMxNTY1YzAnLFxyXG4gICAgfSxcclxuICB9LFxyXG4gIGZvbnRXZWlnaHRzOiB7XHJcbiAgICBub3JtYWw6IDQwMCxcclxuICAgIG1lZGl1bTogNjAwLFxyXG4gICAgYm9sZDogNzAwLFxyXG4gIH0sXHJcbiAgY29tcG9uZW50czoge1xyXG4gICAgQnV0dG9uOiB7XHJcbiAgICAgIGJhc2VTdHlsZTogeyBib3JkZXJSYWRpdXM6ICdtZCcgfSxcclxuICAgIH0sXHJcbiAgICBUYWJsZToge1xyXG4gICAgICBiYXNlU3R5bGU6IHtcclxuICAgICAgICB0aDogeyBmb250V2VpZ2h0OiAnbWVkaXVtJyB9LFxyXG4gICAgICB9LFxyXG4gICAgfSxcclxuICB9LFxyXG59KTtcclxuXHJcbmV4cG9ydCBkZWZhdWx0IHRoZW1lO1xyXG4iXSwibmFtZXMiOlsiZXh0ZW5kVGhlbWUiLCJ0aGVtZSIsImZvbnRzIiwiaGVhZGluZyIsImJvZHkiLCJjb2xvcnMiLCJicmFuZCIsImZvbnRXZWlnaHRzIiwibm9ybWFsIiwibWVkaXVtIiwiYm9sZCIsImNvbXBvbmVudHMiLCJCdXR0b24iLCJiYXNlU3R5bGUiLCJib3JkZXJSYWRpdXMiLCJUYWJsZSIsInRoIiwiZm9udFdlaWdodCJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./theme.tsx\n");

/***/ }),

/***/ "next/dist/compiled/next-server/pages.runtime.dev.js":
/*!**********************************************************************!*\
  !*** external "next/dist/compiled/next-server/pages.runtime.dev.js" ***!
  \**********************************************************************/
/***/ ((module) => {

module.exports = require("next/dist/compiled/next-server/pages.runtime.dev.js");

/***/ }),

/***/ "react":
/*!************************!*\
  !*** external "react" ***!
  \************************/
/***/ ((module) => {

module.exports = require("react");

/***/ }),

/***/ "react/jsx-runtime":
/*!************************************!*\
  !*** external "react/jsx-runtime" ***!
  \************************************/
/***/ ((module) => {

module.exports = require("react/jsx-runtime");

/***/ }),

/***/ "path":
/*!***********************!*\
  !*** external "path" ***!
  \***********************/
/***/ ((module) => {

module.exports = require("path");

/***/ }),

/***/ "@chakra-ui/react":
/*!***********************************!*\
  !*** external "@chakra-ui/react" ***!
  \***********************************/
/***/ ((module) => {

module.exports = import("@chakra-ui/react");;

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = __webpack_require__.X(0, ["vendor-chunks/next"], () => (__webpack_exec__("./pages/_document.tsx")));
module.exports = __webpack_exports__;

})();