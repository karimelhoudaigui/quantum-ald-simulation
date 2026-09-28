(async ()=>{
    function Xe(t, e) {
        const n = l.boys_eval(t, e);
        if (n[2]) throw _(n[1]);
        return _(n[0]);
    }
    function e0(t, e) {
        const n = l.boys_eval_all(t, e);
        if (n[2]) throw _(n[1]);
        return _(n[0]);
    }
    function t0(t, e) {
        const n = Be(e, l.__wbindgen_malloc), r = S, o = l.boys_eval_many(t, n, r);
        if (o[2]) throw _(o[1]);
        return _(o[0]);
    }
    function n0(t) {
        const e = l.compute_difference_density(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function r0(t) {
        const e = l.compute_dipole(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function o0(t) {
        const e = l.compute_integral_matrices(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function i0(t, e) {
        const n = E(t, l.__wbindgen_malloc, l.__wbindgen_realloc), r = S, o = E(e, l.__wbindgen_malloc, l.__wbindgen_realloc), i = S, a = l.compute_integrals(n, r, o, i);
        if (a[2]) throw _(a[1]);
        return _(a[0]);
    }
    function s0(t, e, n) {
        const r = E(t, l.__wbindgen_malloc, l.__wbindgen_realloc), o = S, i = E(e, l.__wbindgen_malloc, l.__wbindgen_realloc), a = S, c = l.compute_integrals_with_options(r, o, i, a, n);
        if (c[2]) throw _(c[1]);
        return _(c[0]);
    }
    function a0(t, e, n, r) {
        const o = E(t, l.__wbindgen_malloc, l.__wbindgen_realloc), i = S, a = E(e, l.__wbindgen_malloc, l.__wbindgen_realloc), c = S, s = l.compute_integrals_with_options_and_progress(o, i, a, c, n, D(r) ? 0 : U(r));
        if (s[2]) throw _(s[1]);
        return _(s[0]);
    }
    function c0(t, e, n) {
        const r = E(t, l.__wbindgen_malloc, l.__wbindgen_realloc), o = S, i = E(e, l.__wbindgen_malloc, l.__wbindgen_realloc), a = S, c = l.compute_integrals_with_progress(r, o, i, a, D(n) ? 0 : U(n));
        if (c[2]) throw _(c[1]);
        return _(c[0]);
    }
    function l0(t) {
        const e = l.compute_population(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function u0(t) {
        const e = l.dual_marching_cubes(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function d0(t, e, n, r, o, i, a, c, s) {
        const f = Be(t, l.__wbindgen_malloc), m = S, g = l.dual_marching_cubes_typed(f, m, e, n, r, o, i, a, c, s);
        if (g[2]) throw _(g[1]);
        return _(g[0]);
    }
    function f0(t) {
        const e = l.eri_detail(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function _0(t) {
        const e = l.evaluate_density_grid(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function m0(t) {
        const e = l.evaluate_mo_grid(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function g0(t) {
        const e = l.evaluate_radial_profile(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function p0(t) {
        const e = l.fock_decomposition(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function b0(t, e) {
        const n = E(e, l.__wbindgen_malloc, l.__wbindgen_realloc), r = S, o = l.get_basis_info(t, n, r);
        if (o[2]) throw _(o[1]);
        return _(o[0]);
    }
    function y0() {
        return l.has_threading_support() !== 0;
    }
    function h0() {
        l.init();
    }
    function A0(t) {
        const e = l.integral_with_breakdown(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function w0(t, e, n) {
        const r = l.ks_scf(t, D(e) ? 0 : U(e), D(n) ? 0 : U(n));
        if (r[2]) throw _(r[1]);
        return _(r[0]);
    }
    function I0(t) {
        const e = l.marching_cubes(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function R0(t, e, n) {
        const r = l.optimize_geometry(t, e, D(n) ? 0 : U(n));
        if (r[2]) throw _(r[1]);
        return _(r[0]);
    }
    function S0(t) {
        const e = l.overlap_vs_distance(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function M0(t, e) {
        const n = l.pes_scan(t, e);
        if (n[2]) throw _(n[1]);
        return _(n[0]);
    }
    function v0(t, e) {
        const n = l.pes_scan_internal(t, e);
        if (n[2]) throw _(n[1]);
        return _(n[0]);
    }
    function E0(t, e) {
        const n = l.rys_compute(t, e);
        if (n[2]) throw _(n[1]);
        return _(n[0]);
    }
    function D0(t, e) {
        const n = l.rys_error_curve(t, e);
        if (n[2]) throw _(n[1]);
        return _(n[0]);
    }
    function N0(t, e) {
        const n = E(t, l.__wbindgen_malloc, l.__wbindgen_realloc), r = S, o = l.scf_run(n, r, e);
        if (o[2]) throw _(o[1]);
        return _(o[0]);
    }
    function $0(t) {
        const e = l.test_compute(t);
        if (e[2]) throw _(e[1]);
        return _(e[0]);
    }
    function x0() {
        let t, e;
        try {
            const n = l.version();
            return t = n[0], e = n[1], q(n[0], n[1]);
        } finally{
            l.__wbindgen_free(t, e, 1);
        }
    }
    function ze() {
        return {
            __proto__: null,
            "./qc_wasm_bg.js": {
                __proto__: null,
                __wbg_Error_8c4e43fe74559d73: function(e, n) {
                    return Error(q(e, n));
                },
                __wbg_Number_04624de7d0e8332d: function(e) {
                    return Number(e);
                },
                __wbg_String_8f0eb39a4a4c2f66: function(e, n) {
                    const r = String(n), o = E(r, l.__wbindgen_malloc, l.__wbindgen_realloc), i = S;
                    x().setInt32(e + 4, i, !0), x().setInt32(e + 0, o, !0);
                },
                __wbg___wbindgen_bigint_get_as_i64_8fcf4ce7f1ca72a2: function(e, n) {
                    const r = n, o = typeof r == "bigint" ? r : void 0;
                    x().setBigInt64(e + 8, D(o) ? BigInt(0) : o, !0), x().setInt32(e + 0, !D(o), !0);
                },
                __wbg___wbindgen_boolean_get_bbbb1c18aa2f5e25: function(e) {
                    const n = e, r = typeof n == "boolean" ? n : void 0;
                    return D(r) ? 16777215 : r ? 1 : 0;
                },
                __wbg___wbindgen_debug_string_0bc8482c6e3508ae: function(e, n) {
                    const r = ce(n), o = E(r, l.__wbindgen_malloc, l.__wbindgen_realloc), i = S;
                    x().setInt32(e + 4, i, !0), x().setInt32(e + 0, o, !0);
                },
                __wbg___wbindgen_in_47fa6863be6f2f25: function(e, n) {
                    return e in n;
                },
                __wbg___wbindgen_is_bigint_31b12575b56f32fc: function(e) {
                    return typeof e == "bigint";
                },
                __wbg___wbindgen_is_function_0095a73b8b156f76: function(e) {
                    return typeof e == "function";
                },
                __wbg___wbindgen_is_null_ac34f5003991759a: function(e) {
                    return e === null;
                },
                __wbg___wbindgen_is_object_5ae8e5880f2c1fbd: function(e) {
                    const n = e;
                    return typeof n == "object" && n !== null;
                },
                __wbg___wbindgen_is_undefined_9e4d92534c42d778: function(e) {
                    return e === void 0;
                },
                __wbg___wbindgen_jsval_eq_11888390b0186270: function(e, n) {
                    return e === n;
                },
                __wbg___wbindgen_jsval_loose_eq_9dd77d8cd6671811: function(e, n) {
                    return e == n;
                },
                __wbg___wbindgen_number_get_8ff4255516ccad3e: function(e, n) {
                    const r = n, o = typeof r == "number" ? r : void 0;
                    x().setFloat64(e + 8, D(o) ? 0 : o, !0), x().setInt32(e + 0, !D(o), !0);
                },
                __wbg___wbindgen_string_get_72fb696202c56729: function(e, n) {
                    const r = n, o = typeof r == "string" ? r : void 0;
                    var i = D(o) ? 0 : E(o, l.__wbindgen_malloc, l.__wbindgen_realloc), a = S;
                    x().setInt32(e + 4, a, !0), x().setInt32(e + 0, i, !0);
                },
                __wbg___wbindgen_throw_be289d5034ed271b: function(e, n) {
                    throw new Error(q(e, n));
                },
                __wbg_call_389efe28435a9388: function() {
                    return G(function(e, n) {
                        return e.call(n);
                    }, arguments);
                },
                __wbg_call_4708e0c13bdc8e95: function() {
                    return G(function(e, n, r) {
                        return e.call(n, r);
                    }, arguments);
                },
                __wbg_done_57b39ecd9addfe81: function(e) {
                    return e.done;
                },
                __wbg_error_ce76b08a8bf51178: function(e, n) {
                    console.error(q(e, n));
                },
                __wbg_get_9b94d73e6221f75c: function(e, n) {
                    return e[n >>> 0];
                },
                __wbg_get_b3ed3ad4be2bc8ac: function() {
                    return G(function(e, n) {
                        return Reflect.get(e, n);
                    }, arguments);
                },
                __wbg_get_index_253dd2a9e007656d: function(e, n) {
                    return e[n >>> 0];
                },
                __wbg_get_with_ref_key_1dc361bd10053bfe: function(e, n) {
                    return e[n];
                },
                __wbg_instanceof_ArrayBuffer_c367199e2fa2aa04: function(e) {
                    let n;
                    try {
                        n = e instanceof ArrayBuffer;
                    } catch  {
                        n = !1;
                    }
                    return n;
                },
                __wbg_instanceof_Uint8Array_9b9075935c74707c: function(e) {
                    let n;
                    try {
                        n = e instanceof Uint8Array;
                    } catch  {
                        n = !1;
                    }
                    return n;
                },
                __wbg_isArray_d314bb98fcf08331: function(e) {
                    return Array.isArray(e);
                },
                __wbg_isSafeInteger_bfbc7332a9768d2a: function(e) {
                    return Number.isSafeInteger(e);
                },
                __wbg_iterator_6ff6560ca1568e55: function() {
                    return Symbol.iterator;
                },
                __wbg_length_32ed9a279acd054c: function(e) {
                    return e.length;
                },
                __wbg_length_35a7bace40f36eac: function(e) {
                    return e.length;
                },
                __wbg_new_361308b2356cecd0: function() {
                    return new Object;
                },
                __wbg_new_3eb36ae241fe6f44: function() {
                    return new Array;
                },
                __wbg_new_dd2b680c8bf6ae29: function(e) {
                    return new Uint8Array(e);
                },
                __wbg_new_from_slice_132ef6dc5072cf68: function(e, n) {
                    return new Float32Array(P0(e, n));
                },
                __wbg_new_from_slice_19d21922ff3c0ae6: function(e, n) {
                    return new Uint32Array(O0(e, n));
                },
                __wbg_new_from_slice_38c66b2d6c31f4b7: function(e, n) {
                    return new Float64Array(W0(e, n));
                },
                __wbg_next_3482f54c49e8af19: function() {
                    return G(function(e) {
                        return e.next();
                    }, arguments);
                },
                __wbg_next_418f80d8f5303233: function(e) {
                    return e.next;
                },
                __wbg_now_a3af9a2f4bbaa4d1: function() {
                    return Date.now();
                },
                __wbg_of_ddc0942b0dce16a1: function(e, n, r) {
                    return Array.of(e, n, r);
                },
                __wbg_prototypesetcall_bdcdcc5842e4d77d: function(e, n, r) {
                    Uint8Array.prototype.set.call(T0(e, n), r);
                },
                __wbg_set_3f1d0b984ed272ed: function(e, n, r) {
                    e[n] = r;
                },
                __wbg_set_6cb8631f80447a67: function() {
                    return G(function(e, n, r) {
                        return Reflect.set(e, n, r);
                    }, arguments);
                },
                __wbg_set_f43e577aea94465b: function(e, n, r) {
                    e[n >>> 0] = r;
                },
                __wbg_value_0546255b415e96c1: function(e) {
                    return e.value;
                },
                __wbindgen_cast_0000000000000001: function(e) {
                    return e;
                },
                __wbindgen_cast_0000000000000002: function(e, n) {
                    return q(e, n);
                },
                __wbindgen_cast_0000000000000003: function(e) {
                    return BigInt.asUintN(64, e);
                },
                __wbindgen_init_externref_table: function() {
                    const e = l.__wbindgen_externrefs, n = e.grow(4);
                    e.set(0, void 0), e.set(n + 0, void 0), e.set(n + 1, null), e.set(n + 2, !0), e.set(n + 3, !1);
                }
            }
        };
    }
    function U(t) {
        const e = l.__externref_table_alloc();
        return l.__wbindgen_externrefs.set(e, t), e;
    }
    function ce(t) {
        const e = typeof t;
        if (e == "number" || e == "boolean" || t == null) return `${t}`;
        if (e == "string") return `"${t}"`;
        if (e == "symbol") {
            const o = t.description;
            return o == null ? "Symbol" : `Symbol(${o})`;
        }
        if (e == "function") {
            const o = t.name;
            return typeof o == "string" && o.length > 0 ? `Function(${o})` : "Function";
        }
        if (Array.isArray(t)) {
            const o = t.length;
            let i = "[";
            o > 0 && (i += ce(t[0]));
            for(let a = 1; a < o; a++)i += ", " + ce(t[a]);
            return i += "]", i;
        }
        const n = /\[object ([^\]]+)\]/.exec(toString.call(t));
        let r;
        if (n && n.length > 1) r = n[1];
        else return toString.call(t);
        if (r == "Object") try {
            return "Object(" + JSON.stringify(t) + ")";
        } catch  {
            return "Object";
        }
        return t instanceof Error ? `${t.name}: ${t.message}
${t.stack}` : r;
    }
    function P0(t, e) {
        return t = t >>> 0, L0().subarray(t / 4, t / 4 + e);
    }
    function W0(t, e) {
        return t = t >>> 0, je().subarray(t / 8, t / 8 + e);
    }
    function O0(t, e) {
        return t = t >>> 0, k0().subarray(t / 4, t / 4 + e);
    }
    function T0(t, e) {
        return t = t >>> 0, X().subarray(t / 1, t / 1 + e);
    }
    let z = null;
    function x() {
        return (z === null || z.buffer.detached === !0 || z.buffer.detached === void 0 && z.buffer !== l.memory.buffer) && (z = new DataView(l.memory.buffer)), z;
    }
    let Y = null;
    function L0() {
        return (Y === null || Y.byteLength === 0) && (Y = new Float32Array(l.memory.buffer)), Y;
    }
    let Q = null;
    function je() {
        return (Q === null || Q.byteLength === 0) && (Q = new Float64Array(l.memory.buffer)), Q;
    }
    function q(t, e) {
        return t = t >>> 0, C0(t, e);
    }
    let J = null;
    function k0() {
        return (J === null || J.byteLength === 0) && (J = new Uint32Array(l.memory.buffer)), J;
    }
    let Z = null;
    function X() {
        return (Z === null || Z.byteLength === 0) && (Z = new Uint8Array(l.memory.buffer)), Z;
    }
    function G(t, e) {
        try {
            return t.apply(this, e);
        } catch (n) {
            const r = U(n);
            l.__wbindgen_exn_store(r);
        }
    }
    function D(t) {
        return t == null;
    }
    function Be(t, e) {
        const n = e(t.length * 8, 8) >>> 0;
        return je().set(t, n / 8), S = t.length, n;
    }
    function E(t, e, n) {
        if (n === void 0) {
            const c = ee.encode(t), s = e(c.length, 1) >>> 0;
            return X().subarray(s, s + c.length).set(c), S = c.length, s;
        }
        let r = t.length, o = e(r, 1) >>> 0;
        const i = X();
        let a = 0;
        for(; a < r; a++){
            const c = t.charCodeAt(a);
            if (c > 127) break;
            i[o + a] = c;
        }
        if (a !== r) {
            a !== 0 && (t = t.slice(a)), o = n(o, r, r = a + t.length * 3, 1) >>> 0;
            const c = X().subarray(o + a, o + r), s = ee.encodeInto(t, c);
            a += s.written, o = n(o, r, a, 1) >>> 0;
        }
        return S = a, o;
    }
    function _(t) {
        const e = l.__wbindgen_externrefs.get(t);
        return l.__externref_table_dealloc(t), e;
    }
    let te = new TextDecoder("utf-8", {
        ignoreBOM: !0,
        fatal: !0
    });
    te.decode();
    const F0 = 2146435072;
    let se = 0;
    function C0(t, e) {
        return se += e, se >= F0 && (te = new TextDecoder("utf-8", {
            ignoreBOM: !0,
            fatal: !0
        }), te.decode(), se = e), te.decode(X().subarray(t, t + e));
    }
    const ee = new TextEncoder;
    "encodeInto" in ee || (ee.encodeInto = function(t, e) {
        const n = ee.encode(t);
        return e.set(n), {
            read: t.length,
            written: n.length
        };
    });
    let S = 0, l;
    function Ke(t, e) {
        return l = t.exports, z = null, Y = null, Q = null, J = null, Z = null, l.__wbindgen_start(), l;
    }
    async function V0(t, e) {
        if (typeof Response == "function" && t instanceof Response) {
            if (typeof WebAssembly.instantiateStreaming == "function") try {
                return await WebAssembly.instantiateStreaming(t, e);
            } catch (o) {
                if (t.ok && n(t.type) && t.headers.get("Content-Type") !== "application/wasm") console.warn("`WebAssembly.instantiateStreaming` failed because your server does not serve Wasm with `application/wasm` MIME type. Falling back to `WebAssembly.instantiate` which is slower. Original error:\n", o);
                else throw o;
            }
            const r = await t.arrayBuffer();
            return await WebAssembly.instantiate(r, e);
        } else {
            const r = await WebAssembly.instantiate(t, e);
            return r instanceof WebAssembly.Instance ? {
                instance: r,
                module: t
            } : r;
        }
        function n(r) {
            switch(r){
                case "basic":
                case "cors":
                case "default":
                    return !0;
            }
            return !1;
        }
    }
    function H0(t) {
        if (l !== void 0) return l;
        t !== void 0 && (Object.getPrototypeOf(t) === Object.prototype ? { module: t } = t : console.warn("using deprecated parameters for `initSync()`; pass a single object instead"));
        const e = ze();
        t instanceof WebAssembly.Module || (t = new WebAssembly.Module(t));
        const n = new WebAssembly.Instance(t, e);
        return Ke(n);
    }
    async function Ue(t) {
        if (l !== void 0) return l;
        t !== void 0 && (Object.getPrototypeOf(t) === Object.prototype ? { module_or_path: t } = t : console.warn("using deprecated parameters for the initialization function; pass a single object instead")), t === void 0 && (t = new URL("./qc_wasm_bg.wasm", import.meta.url));
        const e = ze();
        (typeof t == "string" || typeof Request == "function" && t instanceof Request || typeof URL == "function" && t instanceof URL) && (t = fetch(t));
        const { instance: n, module: r } = await V0(await t, e);
        return Ke(n);
    }
    var Ge = Object.freeze({
        __proto__: null,
        boys_eval: Xe,
        boys_eval_all: e0,
        boys_eval_many: t0,
        compute_difference_density: n0,
        compute_dipole: r0,
        compute_integral_matrices: o0,
        compute_integrals: i0,
        compute_integrals_with_options: s0,
        compute_integrals_with_options_and_progress: a0,
        compute_integrals_with_progress: c0,
        compute_population: l0,
        default: Ue,
        dual_marching_cubes: u0,
        dual_marching_cubes_typed: d0,
        eri_detail: f0,
        evaluate_density_grid: _0,
        evaluate_mo_grid: m0,
        evaluate_radial_profile: g0,
        fock_decomposition: p0,
        get_basis_info: b0,
        has_threading_support: y0,
        init: h0,
        initSync: H0,
        integral_with_breakdown: A0,
        ks_scf: w0,
        marching_cubes: I0,
        optimize_geometry: R0,
        overlap_vs_distance: S0,
        pes_scan: M0,
        pes_scan_internal: v0,
        rys_compute: E0,
        rys_error_curve: D0,
        scf_run: N0,
        test_compute: $0,
        version: x0
    });
    function z0(t) {
        throw new Error(`Unexpected value: ${JSON.stringify(t)}`);
    }
    function j0(t, e, n) {
        return {
            type: "pong",
            requestId: t.requestId,
            wasmVersion: e,
            threadsAvailable: n.threadsAvailable,
            numThreads: n.numThreads
        };
    }
    let le = null, ue = null, de = null;
    function B0(t, e, n) {
        le = t, ue = e, de = n;
    }
    function v(t, e, n) {
        return {
            type: "error",
            requestId: t,
            code: e,
            message: n
        };
    }
    function K0(t) {
        const { requestId: e, m: n, T: r } = t;
        if (n < 0 || !Number.isInteger(n)) return v(e, "INVALID_PARAMS", `Invalid order m=${n}: must be a non-negative integer`);
        if (r < 0) return v(e, "INVALID_PARAMS", `Invalid argument T=${r}: must be >= 0`);
        if (!le) return v(e, "WORKER_NOT_READY", "Boys WASM function not initialized");
        try {
            return le(n, r);
        } catch (o) {
            const i = o instanceof Error ? o.message : "Unknown WASM error";
            return v(e, "HANDLER_ERROR", `Boys evaluation failed: ${i}`);
        }
    }
    function U0(t) {
        const { requestId: e, m: n, T_range: r, points: o } = t;
        if (n < 0 || !Number.isInteger(n)) return v(e, "INVALID_PARAMS", `Invalid order m=${n}: must be a non-negative integer`);
        if (r[0] < 0) return v(e, "INVALID_PARAMS", `Invalid T_min=${r[0]}: must be >= 0`);
        if (r[1] < r[0]) return v(e, "INVALID_PARAMS", `Invalid range: T_max=${r[1]} must be >= T_min=${r[0]}`);
        if (o < 1 || !Number.isInteger(o)) return v(e, "INVALID_PARAMS", `Invalid points=${o}: must be a positive integer`);
        if (!ue) return v(e, "WORKER_NOT_READY", "Boys WASM function not initialized");
        try {
            const [i, a] = r, c = [];
            if (o === 1) c.push(i);
            else {
                const m = (a - i) / (o - 1);
                for(let g = 0; g < o; g++)c.push(i + g * m);
            }
            const s = new Float64Array(c);
            return {
                results: ue(n, s),
                m: n,
                T_range: r,
                points: o
            };
        } catch (i) {
            const a = i instanceof Error ? i.message : "Unknown WASM error";
            return v(e, "HANDLER_ERROR", `Boys sweep failed: ${a}`);
        }
    }
    function G0(t) {
        const { requestId: e, mMax: n, T: r } = t;
        if (n < 0 || !Number.isInteger(n)) return v(e, "INVALID_PARAMS", `Invalid mMax=${n}: must be a non-negative integer`);
        if (r < 0) return v(e, "INVALID_PARAMS", `Invalid argument T=${r}: must be >= 0`);
        if (!de) return v(e, "WORKER_NOT_READY", "Boys WASM function not initialized");
        try {
            return {
                results: de(n, r),
                mMax: n,
                T: r
            };
        } catch (o) {
            const i = o instanceof Error ? o.message : "Unknown WASM error";
            return v(e, "HANDLER_ERROR", `Boys eval_all failed: ${i}`);
        }
    }
    let fe = null, _e = null;
    function Y0(t, e) {
        fe = t, _e = e;
    }
    function k(t, e, n) {
        return {
            type: "error",
            requestId: t,
            code: e,
            message: n
        };
    }
    function Q0(t) {
        const { requestId: e, n, T: r } = t;
        if (n < 1 || !Number.isInteger(n)) return k(e, "INVALID_PARAMS", `Invalid order n=${n}: must be a positive integer`);
        if (r < 0) return k(e, "INVALID_PARAMS", `Invalid argument T=${r}: must be >= 0`);
        if (!fe) return k(e, "WORKER_NOT_READY", "Rys WASM function not initialized");
        try {
            return fe(n, r);
        } catch (o) {
            const i = o instanceof Error ? o.message : "Unknown WASM error";
            return k(e, "HANDLER_ERROR", `Rys compute failed: ${i}`);
        }
    }
    function q0(t) {
        const { requestId: e, T: n, max_order: r } = t;
        if (r < 1 || !Number.isInteger(r)) return k(e, "INVALID_PARAMS", `Invalid max_order=${r}: must be a positive integer`);
        if (n < 0) return k(e, "INVALID_PARAMS", `Invalid argument T=${n}: must be >= 0`);
        if (!_e) return k(e, "WORKER_NOT_READY", "Rys WASM function not initialized");
        try {
            return _e(r, n);
        } catch (o) {
            const i = o instanceof Error ? o.message : "Unknown WASM error";
            return k(e, "HANDLER_ERROR", `Rys error curve failed: ${i}`);
        }
    }
    const J0 = 1, Z0 = "h2_sto3g_r1.4", X0 = "H2 (STO-3G, R=1.4 bohr)", et = "Hydrogen molecule at equilibrium bond length. Reference system for IQCP Module E.", tt = {
        atoms: [
            {
                symbol: "H",
                xyz: [
                    0,
                    0,
                    0
                ]
            },
            {
                symbol: "H",
                xyz: [
                    0,
                    0,
                    1.4
                ]
            }
        ],
        units: "bohr"
    }, nt = "sto-3g", rt = 2, ot = 2, it = .7142857142857143, st = [
        1.0000000000000002,
        .659318206134864,
        .659318206134864,
        1.0000000000000002
    ], at = [
        -1.1204090089068204,
        -.958379964389617,
        -.958379964389617,
        -1.1204090089068204
    ], ct = [
        .7746059439198978,
        .44410765803196084,
        .2970285402769315,
        .5696759256037501,
        .44410765803196095,
        .7746059439198978
    ], lt = "8-fold symmetry: pair(i,j)=i*(i+1)/2+j, idx(P,Q)=P*(P+1)/2+Q", ut = {
        software: "PySCF",
        version: "2.11.0",
        energy: -1.116714325062551
    };
    var We = {
        format_version: J0,
        system_id: Z0,
        label: X0,
        description: et,
        geometry: tt,
        basis_id: nt,
        nbf: rt,
        nelec: ot,
        e_nuc: it,
        s_matrix: st,
        h_core: at,
        eri_compressed: ct,
        eri_indexing: lt,
        reference: ut
    };
    const dt = 1, ft = "heh_plus_sto3g", _t = "HeH+ (STO-3G)", mt = "Helium hydride ion - heteronuclear diatomic with 2 electrons. Good comparison to H2 as same basis size but different nuclear charges.", gt = {
        atoms: [
            {
                symbol: "He",
                xyz: [
                    0,
                    0,
                    0
                ]
            },
            {
                symbol: "H",
                xyz: [
                    0,
                    0,
                    1.4632
                ]
            }
        ],
        units: "bohr"
    }, pt = "sto-3g", bt = 2, yt = 2, ht = 1.366867140513942, At = [
        1.0000000000000002,
        .5368193496887589,
        .536819349688759,
        1.0000000000000002
    ], wt = [
        -2.5982830075866272,
        -1.4318285046320312,
        -1.4318285046320314,
        -1.731825672645799
    ], It = [
        1.0557129427350722,
        .4439649874114326,
        .22431933879949295,
        .5908073084285695,
        .36741015713128483,
        .7746059439198978
    ], Rt = "8-fold symmetry: pair(i,j)=i*(i+1)/2+j, idx(P,Q)=P*(P+1)/2+Q", St = {
        software: "PySCF",
        version: "2.11.0",
        energy: -2.8418364992873766
    };
    var Mt = {
        format_version: dt,
        system_id: ft,
        label: _t,
        description: mt,
        geometry: gt,
        basis_id: pt,
        nbf: bt,
        nelec: yt,
        e_nuc: ht,
        s_matrix: At,
        h_core: wt,
        eri_compressed: It,
        eri_indexing: Rt,
        reference: St
    };
    const vt = 1, Et = "lih_sto3g", Dt = "LiH (STO-3G)", Nt = "Lithium hydride - polar diatomic with 4 electrons. First system with core and valence orbitals.", $t = {
        atoms: [
            {
                symbol: "Li",
                xyz: [
                    0,
                    0,
                    0
                ]
            },
            {
                symbol: "H",
                xyz: [
                    0,
                    0,
                    3.0139
                ]
            }
        ],
        units: "bohr"
    }, xt = "sto-3g", Pt = 6, Wt = 4, Ot = .995388035435814, Tt = [
        1,
        .2411366511839204,
        0,
        0,
        0,
        .06724681376959651,
        .24113665118392041,
        1,
        0,
        0,
        0,
        .39654816059644865,
        0,
        0,
        .9999999999999998,
        0,
        0,
        0,
        0,
        0,
        0,
        .9999999999999998,
        0,
        0,
        0,
        0,
        0,
        0,
        .9999999999999998,
        .5138664433239561,
        .06724681376959651,
        .3965481605964486,
        0,
        0,
        .513866443323956,
        1.0000000000000002
    ], Lt = [
        -4.737890961895568,
        -1.0645844698857883,
        0,
        0,
        -.016201904922297415,
        -.30558037688906703,
        -1.0645844698857883,
        -1.396423824171874,
        0,
        0,
        -.12244610205976394,
        -.6963752184247414,
        0,
        0,
        -1.136278198610012,
        0,
        0,
        0,
        0,
        0,
        0,
        -1.136278198610012,
        0,
        0,
        -.016201904922297415,
        -.12244610205976394,
        0,
        0,
        -1.2346733164930508,
        -.8408652468444218,
        -.30558037688906703,
        -.6963752184247413,
        0,
        0,
        -.8408652468444214,
        -1.4593098193127234
    ], kt = [
        1.6803951695337487,
        .265420364607807,
        .049941457240236346,
        .3977268610897302,
        .09286014364195108,
        .29056229500912606,
        0,
        0,
        0,
        .008981319284152243,
        0,
        0,
        0,
        .013788268908950862,
        .06418432858622225,
        .3966396422885507,
        .0928803968305991,
        .2904969755879808,
        0,
        0,
        .312945511159409,
        0,
        0,
        0,
        0,
        0,
        0,
        .008981319284152243,
        0,
        0,
        0,
        0,
        0,
        0,
        .013788268908950862,
        .06418432858622225,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .016869139513691025,
        .3966396422885507,
        .0928803968305991,
        .2904969755879808,
        0,
        0,
        .27920723213202703,
        0,
        0,
        0,
        .312945511159409,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .008981319284152243,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .013788268908950862,
        .06418432858622225,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .016869139513691022,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .016869139513691022,
        .3966396422885507,
        .0928803968305991,
        .2904969755879808,
        0,
        0,
        .27920723213202703,
        0,
        0,
        0,
        .27920723213202703,
        0,
        0,
        0,
        0,
        .312945511159409,
        .07201963455017794,
        .013617220845219054,
        .025752710293660924,
        0,
        0,
        .02544951687464705,
        0,
        0,
        0,
        .02544951687464705,
        .001608375653695285,
        .0031075377048122295,
        0,
        0,
        .026371056654611987,
        .004058059346313234,
        .15144905574727463,
        .035697711527732295,
        .1160005907734807,
        0,
        0,
        .11026301508432415,
        0,
        0,
        0,
        .11026301508432415,
        .005827954658415537,
        .03376426267313101,
        0,
        0,
        .12735337745121547,
        .011591823148795314,
        .07430593447572514,
        0,
        0,
        0,
        .003036712994618079,
        .013657729679676236,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .0053550159957405415,
        0,
        0,
        0,
        0,
        .005668485896617132,
        0,
        0,
        0,
        0,
        0,
        0,
        .003036712994618079,
        .013657729679676236,
        0,
        0,
        0,
        0,
        0,
        .0053550159957405415,
        0,
        0,
        0,
        0,
        .005668485896617132,
        .1825690566038291,
        .04352680968791456,
        .1469841416519565,
        0,
        0,
        .13716740037417524,
        0,
        0,
        0,
        .13716740037417524,
        .009072574957101913,
        .05164941669266843,
        0,
        0,
        .16643641726902295,
        .0147699797814884,
        .10356254880189823,
        0,
        0,
        .1467503904246957,
        .33052477936118946,
        .07933183229985784,
        .2814542815964561,
        0,
        0,
        .2570657841418212,
        0,
        0,
        0,
        .2570657841418212,
        .01531930376474423,
        .10587397821497099,
        0,
        0,
        .32982990279573454,
        .02706628682333179,
        .22284894363217833,
        0,
        0,
        .3233187440322019,
        .7746059439198978
    ], Ft = "8-fold symmetry: pair(i,j)=i*(i+1)/2+j, idx(P,Q)=P*(P+1)/2+Q", Ct = {
        software: "PySCF",
        version: "2.11.0",
        energy: -7.862027355989619
    };
    var Vt = {
        format_version: vt,
        system_id: Et,
        label: Dt,
        description: Nt,
        geometry: $t,
        basis_id: xt,
        nbf: Pt,
        nelec: Wt,
        e_nuc: Ot,
        s_matrix: Tt,
        h_core: Lt,
        eri_compressed: kt,
        eri_indexing: Ft,
        reference: Ct
    };
    const Ht = 1, zt = "h2o_sto3g", jt = "H2O (STO-3G)", Bt = "Water molecule - bent triatomic with 10 electrons. Familiar molecule demonstrating non-linear geometry.", Kt = {
        atoms: [
            {
                symbol: "O",
                xyz: [
                    0,
                    0,
                    .2217282
                ]
            },
            {
                symbol: "H",
                xyz: [
                    0,
                    1.4305447,
                    -.8869128
                ]
            },
            {
                symbol: "H",
                xyz: [
                    0,
                    -1.4305447,
                    -.8869128
                ]
            }
        ],
        units: "bohr"
    }, Ut = "sto-3g", Gt = 7, Yt = 10, Qt = 9.190047775408713, qt = [
        1,
        .2367039365108476,
        0,
        0,
        0,
        .05390986783733549,
        .05390986783733549,
        .23670393651084762,
        1,
        0,
        0,
        0,
        .4744593327948672,
        .4744593327948672,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        .31084805333490506,
        -.31084805333490506,
        0,
        0,
        0,
        0,
        1,
        -.24090047427197664,
        -.24090047427197664,
        .05390986783733551,
        .4744593327948672,
        0,
        .31084805333490517,
        -.2409004742719766,
        1.0000000000000002,
        .25167241066548873,
        .05390986783733551,
        .4744593327948672,
        0,
        -.31084805333490517,
        -.2409004742719766,
        .25167241066548873,
        1.0000000000000002
    ], Jt = [
        -32.72032127988848,
        -7.612663932058798,
        0,
        0,
        .018997247667041316,
        -1.7473476847207985,
        -1.7473476847207985,
        -7.6126639320587985,
        -9.334272567322254,
        0,
        0,
        .22349793728525302,
        -3.738038846106485,
        -3.738038846106485,
        0,
        0,
        -7.457209670074838,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -7.613199551746452,
        0,
        -2.027969572528689,
        2.027969572528689,
        .01899724766704132,
        .22349793728525302,
        0,
        0,
        -7.550895829260635,
        1.6446077652635371,
        1.6446077652635371,
        -1.747347684720799,
        -3.738038846106485,
        0,
        -2.0279695725286895,
        1.6446077652635374,
        -5.074659131269446,
        -1.6073842121435251,
        -1.747347684720799,
        -3.738038846106485,
        0,
        2.027969572528689,
        1.6446077652635371,
        -1.6073842121435251,
        -5.074659131269446
    ], Zt = [
        4.785065404705503,
        .7413803519734079,
        .13687338535438834,
        1.1189468663424704,
        .2566333947309737,
        .8172063215260582,
        0,
        0,
        0,
        .024477412258099275,
        0,
        0,
        0,
        .03780860741636099,
        .18051839210463208,
        1.1158138121524277,
        .25668398581010293,
        .8170226053209142,
        0,
        0,
        .8801590933750454,
        0,
        0,
        0,
        0,
        0,
        0,
        .024477412258099275,
        0,
        0,
        0,
        0,
        0,
        0,
        .03780860741636099,
        .18051839210463208,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .04744444511838415,
        1.1158138121524277,
        .25668398581010293,
        .8170226053209142,
        0,
        0,
        .7852702031382774,
        0,
        0,
        0,
        .8801590933750454,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .024477412258099275,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .03780860741636099,
        .18051839210463208,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .04744444511838415,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        .04744444511838415,
        1.1158138121524277,
        .25668398581010293,
        .8170226053209142,
        0,
        0,
        .7852702031382774,
        0,
        0,
        0,
        .7852702031382774,
        0,
        0,
        0,
        0,
        .8801590933750452,
        .17157778517111918,
        .03139487587749577,
        .0584380291479903,
        0,
        0,
        .05832730439931859,
        .0011411986839211855,
        .0021301369349663994,
        0,
        .058539454685530325,
        -.0008844041365090272,
        -.0016508097522000401,
        0,
        -.0001644118533702778,
        .05845472000648718,
        .007294452953712398,
        .4032779558626998,
        .09358953286300419,
        .3283082492472612,
        0,
        0,
        .3228530860419085,
        .00553117274268813,
        .04165320492643475,
        0,
        .332886100145125,
        -.004286538463724001,
        -.03228032704105475,
        0,
        -.007775367514488741,
        .3288788265983764,
        .021858550008123617,
        .1611501578209144,
        0,
        0,
        0,
        .009962354906547864,
        .05737303633088518,
        0,
        0,
        0,
        .008729575098621406,
        0,
        0,
        0,
        -.0067652306613772625,
        0,
        0,
        0,
        0,
        .02339956432678349,
        .2247215676252125,
        .05284387219236237,
        .1979938244517325,
        0,
        0,
        .18894153578062356,
        .01271051858649937,
        .08127881168704511,
        0,
        .2123235618479114,
        -.00212976702531918,
        -.018526455479950046,
        0,
        -.011355330521551186,
        .19249876324725437,
        .012906439644697999,
        .11804639575954284,
        0,
        .10890914976091322,
        -.17415432279297755,
        -.040952850554905974,
        -.15344090368794008,
        0,
        0,
        -.14642557703325615,
        -.00212976702531918,
        -.018526455479950042,
        0,
        -.1510156768934301,
        .01161287798682412,
        .07173063601284359,
        0,
        .012286802565252183,
        -.16271281220294667,
        -.01000220975558305,
        -.0914833868814133,
        0,
        -.06626806719515929,
        .07475587376843085,
        .5317376088021973,
        .12540850956202287,
        .5030870518459096,
        0,
        0,
        .48259662632234135,
        .009898138977022066,
        .10156887142139329,
        0,
        .520618648382683,
        -.007670842227876359,
        -.07871366422977544,
        0,
        -.029466239369520645,
        .5054323203631251,
        .0295768360710684,
        .3060704854348846,
        0,
        .2561350227442652,
        -.1984990666493853,
        .7746059439198978,
        .17157778517111918,
        .03139487587749577,
        .0584380291479903,
        0,
        0,
        .05832730439931859,
        -.0011411986839211855,
        -.0021301369349663994,
        0,
        .058539454685530325,
        -.0008844041365090272,
        -.0016508097522000401,
        0,
        .0001644118533702778,
        .05845472000648718,
        .0071816157527201645,
        .021174526652843043,
        0,
        .011389844942546109,
        -.009695199475935518,
        .02830198342888763,
        .007294452953712398,
        .4032779558626998,
        .09358953286300419,
        .3283082492472612,
        0,
        0,
        .3228530860419085,
        -.00553117274268813,
        -.04165320492643475,
        0,
        .332886100145125,
        -.004286538463724001,
        -.03228032704105475,
        0,
        .007775367514488741,
        .3288788265983764,
        .021174526652843046,
        .13184030324670434,
        0,
        .06630203594732044,
        -.07280642125950428,
        .20718654834590003,
        .021858550008123617,
        .1611501578209144,
        0,
        0,
        0,
        .009962354906547864,
        .05737303633088518,
        0,
        0,
        0,
        -.008729575098621406,
        0,
        0,
        0,
        -.0067652306613772625,
        0,
        0,
        0,
        0,
        .01854693152791872,
        0,
        0,
        0,
        0,
        0,
        .02339956432678349,
        -.2247215676252125,
        -.05284387219236237,
        -.1979938244517325,
        0,
        0,
        -.18894153578062356,
        .01271051858649937,
        .08127881168704511,
        0,
        -.2123235618479114,
        .00212976702531918,
        .018526455479950046,
        0,
        -.011355330521551186,
        -.19249876324725437,
        -.01138984494254611,
        -.06630203594732044,
        0,
        -.015227898508068946,
        .03575752893863531,
        -.09138796347857836,
        -.012906439644697999,
        -.11804639575954284,
        0,
        .10890914976091322,
        -.17415432279297755,
        -.040952850554905974,
        -.15344090368794008,
        0,
        0,
        -.14642557703325615,
        .00212976702531918,
        .018526455479950042,
        0,
        -.1510156768934301,
        .01161287798682412,
        .07173063601284359,
        0,
        -.012286802565252183,
        -.16271281220294667,
        -.009695199475935518,
        -.07280642125950426,
        0,
        -.03575752893863532,
        .058137441739340864,
        -.1255929867623073,
        -.01000220975558305,
        -.0914833868814133,
        0,
        .06626806719515929,
        .07475587376843085,
        .16065395343574554,
        .03760969369076678,
        .14257846772851498,
        0,
        0,
        .13931630706209217,
        10164395367051604e-35,
        -2168404344971009e-34,
        0,
        .14211761669484813,
        -.0027384645994778167,
        -.024236473205891847,
        0,
        -10842021724855044e-35,
        .14614975296786314,
        .008694543866547218,
        .06910095826694504,
        0,
        .04357954245110433,
        -.044095955022853656,
        .13440564348407116,
        .008694543866547218,
        .06910095826694504,
        0,
        -.04357954245110433,
        -.044095955022853656,
        .03583941549743049,
        .5317376088021973,
        .12540850956202287,
        .5030870518459096,
        0,
        0,
        .48259662632234135,
        -.009898138977022066,
        -.10156887142139329,
        0,
        .520618648382683,
        -.007670842227876359,
        -.07871366422977544,
        0,
        .029466239369520645,
        .5054323203631251,
        .028301983428887637,
        .2071865483459,
        0,
        .09138796347857837,
        -.1255929867623073,
        .34292007761479915,
        .0295768360710684,
        .3060704854348846,
        0,
        -.2561350227442652,
        -.1984990666493853,
        .13440564348407122,
        .7746059439198978
    ], Xt = "8-fold symmetry: pair(i,j)=i*(i+1)/2+j, idx(P,Q)=P*(P+1)/2+Q", en = {
        software: "PySCF",
        version: "2.11.0",
        energy: -74.9630257175466
    };
    var tn = {
        format_version: Ht,
        system_id: zt,
        label: jt,
        description: Bt,
        geometry: Kt,
        basis_id: Ut,
        nbf: Gt,
        nelec: Yt,
        e_nuc: Qt,
        s_matrix: qt,
        h_core: Jt,
        eri_compressed: Zt,
        eri_indexing: Xt,
        reference: en
    };
    const nn = 1, rn = "nh3_sto3g", on = "NH3 (STO-3G)", sn = "Ammonia - pyramidal molecule with 10 electrons. Demonstrates non-planar molecular geometry.", an = {
        atoms: [
            {
                symbol: "N",
                xyz: [
                    0,
                    0,
                    .219705
                ]
            },
            {
                symbol: "H",
                xyz: [
                    0,
                    1.7714918,
                    -.512645
                ]
            },
            {
                symbol: "H",
                xyz: [
                    1.5342036,
                    -.8857459,
                    -.512645
                ]
            },
            {
                symbol: "H",
                xyz: [
                    -1.5342036,
                    -.8857459,
                    -.512645
                ]
            }
        ],
        units: "bohr"
    }, cn = "sto-3g", ln = 8, un = 10, dn = 11.932745473183688, fn = [
        1,
        .23503776528955594,
        0,
        0,
        0,
        .058086975072744865,
        .05808426036240899,
        .05808426036240899,
        .23503776528955594,
        .9999999999999997,
        0,
        0,
        0,
        .49341566385524394,
        .4934033641004471,
        .4934033641004471,
        0,
        0,
        1.0000000000000002,
        0,
        0,
        0,
        .35125478993538534,
        -.35125478993538534,
        0,
        0,
        0,
        1.0000000000000002,
        0,
        .40559595537372617,
        -.2027908747187328,
        -.2027908747187328,
        0,
        0,
        0,
        0,
        1.0000000000000002,
        -.1676768686809323,
        -.1676709958242697,
        -.1676709958242697,
        .058086975072744865,
        .49341566385524394,
        0,
        .4055959553737262,
        -.16767686868093232,
        1.0000000000000002,
        .21444458806736624,
        .21444458806736624,
        .058084260362409004,
        .49340336410044705,
        .3512547899353855,
        -.20279087471873292,
        -.16767099582426973,
        .21444458806736624,
        1.0000000000000002,
        .21443280909436324,
        .058084260362409004,
        .49340336410044705,
        -.3512547899353855,
        -.20279087471873292,
        -.16767099582426973,
        .21444458806736624,
        .21443280909436324,
        1.0000000000000002
    ], _n = [
        -25.76021395472064,
        -5.929197739379027,
        0,
        -8522237254166357e-22,
        .018069981698182115,
        -1.4767535115003227,
        -1.4766845407313332,
        -1.4766845407313332,
        -5.9291977393790285,
        -7.78887497162799,
        0,
        -8245444221392784e-21,
        .2075886734341124,
        -3.3258254115818473,
        -3.3257234197892886,
        -3.3257234197892886,
        0,
        0,
        -6.4774464747718,
        0,
        0,
        0,
        -2.0029924686909557,
        2.0029924686909557,
        -852223725417503e-21,
        -8245444221392784e-21,
        0,
        -6.4774450626077344,
        36031879047937476e-22,
        -2.312880437442258,
        1.1563899275281768,
        1.1563899275281768,
        .018069981698182115,
        .2075886734341124,
        0,
        36031879047937476e-22,
        -6.367941253682191,
        1.0187843764516304,
        1.0187433520402847,
        1.0187433520402847,
        -1.4767535115003234,
        -3.325825411581847,
        0,
        -2.312880437442258,
        1.0187843764516307,
        -4.662534292907366,
        -1.2750417094567086,
        -1.2750417094567086,
        -1.4766845407313336,
        -3.3257234197892878,
        -2.0029924686909566,
        1.1563899275281775,
        1.018743352040285,
        -1.2750417094567084,
        -4.6624661132467615,
        -1.274971371331597,
        -1.4766845407313336,
        -3.3257234197892878,
        2.0029924686909566,
        1.1563899275281773,
        1.018743352040285,
        -1.2750417094567084,
        -1.274971371331597,
        -4.6624661132467615
    ], mn = JSON.parse("[4.166630336662227,0.6408488779669391,0.1174612365518033,0.9698638653761457,0.2209356554223302,0.7082454718774781,0,0,0,0.020960430842605272,0,0,0,0.03245163449288402,0.15644927133410388,0.9671237488757953,0.22097738556347346,0.7080862496655843,0,0,0.7628045369780823,0,0,0,0,0,0,0.020960430842605272,0,0,0,0,0,0,0.03245163449288402,0.15644927133410388,0,0,0,0,0,0,0,0,0.04111851847231425,0.9671237488757953,0.22097738556347346,0.7080862496655843,0,0,0.6805675000334533,0,0,0,0.7628045369780823,0,0,0,0,0,0,0,0,0,0,0.020960430842605272,0,0,0,0,0,0,0,0,0,0,0.03245163449288402,0.15644927133410388,0,0,0,0,0,0,0,0,0,0,0,0,0.04111851847231426,0,0,0,0,0,0,0,0,0,0,0,0,0,0.04111851847231426,0.9671237488757953,0.22097738556347346,0.7080862496655843,0,0,0.6805675000334533,0,0,0,0.6805675000334533,0,0,0,0,0.7628045369780823,0.16063869972561037,0.02920047356844474,0.054581033383204754,0,0,0.054444276837628584,0.0014198832251997105,0.002655038988062269,0,0.0548001938515975,-0.0005869919804172989,-0.0010976160335076906,0,-0.00014713916552147187,0.05450510543862445,0.007381877543596324,0.3727872143302947,0.0858912916493482,0.3018539443794356,0,0,0.2958430997367929,0.006636681298583316,0.04935725603531774,0,0.3110070647025828,-0.002743661330533674,-0.02040471565121833,0,-0.006268913998188507,0.298434722891116,0.02192365950202254,0.16071376489652683,0,0,0,0.008965858459610461,0.051086918991816,0,0,0,0.010089249939153324,0,0,0,-0.004170983005926947,0,0,0,0,0.021872429268638405,0.26463728737124437,0.06176796402746466,0.23110747845356902,0,0,0.21994723651970477,0.013156735478602107,0.08672219931749647,0,0.2512749888539914,-0.0017325447314283542,-0.014731932457441855,0,-0.008780180201272064,0.22185271842259086,0.016502355236133387,0.14784695547422028,0,0.15581999770693442,-0.10940333870375854,-0.025535409452933252,-0.09554182629886926,0,0,-0.09092808595851577,-0.0017325447314283547,-0.014731932457441855,0,-0.09553728315386088,0.009682107405307843,0.05717722702214813,0,0.011994731842039351,-0.10005779463538142,-0.006822216087696417,-0.06112120747132174,0,-0.05537508090400762,0.04476496566087571,0.5057687452219002,0.11840754496002188,0.4735349421781309,0,0,0.45109727657823023,0.012129877520316322,0.12102006125504654,0,0.5081063135113758,-0.0050145960607910585,-0.05003073785615792,0,-0.023568027917481492,0.4608405027367518,0.03060096869172797,0.31180086380448413,0,0.3221156047657139,-0.13316537121434627,0.7746059439198978,0.1606310817632764,0.029199095081101786,0.054578477789660164,0.0012296110941468973,0.0022992523010249167,0.05470865963462208,-0.000709894687533733,-0.0013274335288343648,-0.00015410901233776827,0.05453069904187024,-0.0005869531819626014,-0.0010975449559990573,-0.00012741999165399978,0.0000735637272559943,0.0545025506299232,0.0072277134978012475,0.021022187113140845,0.0006274967728077435,0.014749176768791731,-0.00654673907294528,0.02887963833131587,0.00738118070832392,0.37277521492620264,0.08588855289751798,0.3018450064294769,0.005747421470998269,0.04274408004953387,0.3072072780662092,-0.0033181743306486076,-0.024677554956295516,-0.006566002895264794,0.2996250494247674,-0.0027435238154085812,-0.020403828425559767,-0.00542888453714228,0.003134272543974718,0.29842575191751813,0.021022500534565575,0.12596615479031964,0.013856090992537864,0.08875881155445631,-0.046614938040825143,0.19861127600043066,0.021921937436079935,0.1607051678333361,0.22917965415819158,0.05349194373970358,0.2001428362641521,0.012108655492197922,0.07781171793169991,0.2151944695516927,-0.0018146439559137495,-0.015430124919379139,-0.009225297165374397,0.1928916803353824,-0.0015003789474085448,-0.012757893640498149,-0.007627634944809724,0.00199575280161917,0.19212802582656552,0.013087346310273692,0.08379682433756734,0.02512366443150505,0.05845407074790786,-0.030383964294582656,0.13228916041002192,0.014290600129235045,0.12803479059090972,0.12233015823535554,-0.13231290751373304,-0.03088264807257207,-0.11554900316707901,-0.0018146439559137495,-0.015430124919379142,-0.11415003348297781,0.010013157577253209,0.05999345970505291,0.01115117418399306,-0.12145144347175114,0.0008662178221413603,0.0073655491257531335,0.00199575280161917,-0.005322997817008979,-0.11092179105235737,-0.006831185518427983,-0.03237935649975645,-0.00273065700944476,-0.007047562142579851,0.0116646868203886,-0.03692900707981155,-0.008250430694471981,-0.07391867078349763,-0.05799831715921709,0.05535539314087535,-0.10939859593782186,-0.025534306527355256,-0.09553791044295021,-0.0015003789474085445,-0.01275789364049815,-0.09438121815890857,0.0008662178221413603,0.007365549125753135,0.00199575280161917,-0.09207658103110784,0.009681708138745998,0.057175107254172824,0.0103875196751761,-0.005997054734753954,-0.10005362053542599,-0.00654676936496599,-0.04661454459590959,-0.0050896697496701825,-0.0321449829389874,0.03337215528346934,-0.07945530569752458,-0.006821598518374803,-0.06111723299909656,-0.04795400980298371,0.027685417744784738,0.044761849655863946,0.13248679336050057,0.030724488851903434,0.11466270003727103,0.0016538215600917945,0.013843920302325353,0.11509062044565915,0.0009548268426785996,0.007992678179877338,0.0004196263481855331,0.11460597960820654,-0.0015789078635730263,-0.013216806911547117,-0.0026233064486796275,-0.0015145600501903118,0.11417366069842377,0.007734183329849877,0.05827120875573275,0.005775219754398246,0.049433646235514356,-0.024571485951532263,0.11106113058641706,0.007733824099879121,0.05826984716587052,0.04569815753581898,-0.019714719991769717,-0.02457069453468659,0.025417672815507508,0.5057601202283039,0.11840556176280342,0.47352872944563656,0.010504615786165747,0.10480601144886825,0.49384849344395626,-0.006064658148156859,-0.06050793710573233,-0.02468508572569328,0.4653428764055026,-0.005014364045944412,-0.05002900689620249,-0.020410054995695127,0.011783392068178878,0.46083408129083564,0.02888050944635944,0.19861464510963245,0.03416217780215647,0.1330310968961726,-0.07945710726340403,0.32167365101088186,0.03059901569368727,0.3117911227302078,0.27895669551142077,-0.1610508209776,-0.13315959886796577,0.11106113058641712,0.7746059439198978,0.1606310817632764,0.029199095081101786,0.054578477789660164,-0.0012296110941468973,-0.0022992523010249167,0.05470865963462208,-0.000709894687533733,-0.0013274335288343648,0.00015410901233776827,0.05453069904187024,-0.0005869531819626014,-0.0010975449559990573,0.00012741999165399978,0.0000735637272559943,0.0545025506299232,0.0072277134978012475,0.021022187113140845,-0.0006274967728077435,0.014749176768791731,-0.00654673907294528,0.02887963833131587,0.007227368356957591,0.021021494964789653,0.012459251706006645,-0.007917651733546593,-0.006546451129000819,0.007479620053186032,0.028879119021694842,0.00738118070832392,0.37277521492620264,0.08588855289751798,0.3018450064294769,-0.005747421470998269,-0.04274408004953387,0.3072072780662092,-0.0033181743306486076,-0.024677554956295516,0.006566002895264794,0.2996250494247674,-0.0027435238154085812,-0.020403828425559767,0.00542888453714228,0.003134272543974718,0.29842575191751813,0.021022500534565575,0.12596615479031964,-0.013856090992537864,0.08875881155445631,-0.046614938040825143,0.19861127600043066,0.021021494964789656,0.12596185681367877,0.06993851841998877,-0.05637625227573722,-0.04661285855699265,0.04731924818306487,0.198607456332918,0.021921937436079935,0.1607051678333361,-0.22917965415819158,-0.05349194373970358,-0.2001428362641521,0.012108655492197922,0.07781171793169991,-0.2151944695516927,0.0018146439559137495,0.015430124919379139,-0.009225297165374397,-0.1928916803353824,0.0015003789474085448,0.012757893640498149,-0.007627634944809724,-0.00199575280161917,-0.19212802582656552,-0.013087346310273692,-0.08379682433756734,0.02512366443150505,-0.05845407074790786,0.030383964294582656,-0.13228916041002192,-0.012459251706006647,-0.06993851841998877,-0.023134574965508328,0.03059103505764683,0.025293195852747002,-0.027289800471602385,-0.09812625246194212,-0.014290600129235045,-0.12803479059090972,0.12233015823535554,-0.13231290751373304,-0.03088264807257207,-0.11554900316707901,0.0018146439559137495,0.015430124919379142,-0.11415003348297781,0.010013157577253209,0.05999345970505291,-0.01115117418399306,-0.12145144347175114,0.0008662178221413603,0.0073655491257531335,-0.00199575280161917,-0.005322997817008979,-0.11092179105235737,-0.006831185518427983,-0.03237935649975645,0.00273065700944476,-0.007047562142579851,0.0116646868203886,-0.03692900707981155,-0.007917651733546595,-0.05637625227573721,-0.03059103505764683,0.04120685353557247,0.02047918501340883,-0.015755238520306098,-0.09609549866654718,-0.008250430694471981,-0.07391867078349763,0.05799831715921709,0.05535539314087535,-0.10939859593782186,-0.025534306527355256,-0.09553791044295021,0.0015003789474085445,0.01275789364049815,-0.09438121815890857,0.0008662178221413603,0.007365549125753135,-0.00199575280161917,-0.09207658103110784,0.009681708138745998,0.057175107254172824,-0.0103875196751761,-0.005997054734753954,-0.10005362053542599,-0.00654676936496599,-0.04661454459590959,0.0050896697496701825,-0.0321449829389874,0.03337215528346934,-0.07945530569752458,-0.0065464511290008204,-0.04661285855699263,-0.025293195852747,0.02047918501340883,0.033370701703693106,-0.019402062379085996,-0.07945341711256679,-0.006821598518374803,-0.06111723299909656,0.04795400980298371,0.027685417744784738,0.044761849655863946,0.13248679336050057,0.030724488851903434,0.11466270003727103,-0.0016538215600917945,-0.013843920302325353,0.11509062044565915,0.0009548268426785996,0.007992678179877338,-0.0004196263481855331,0.11460597960820654,-0.0015789078635730263,-0.013216806911547117,0.0026233064486796275,-0.0015145600501903118,0.11417366069842377,0.007734183329849877,0.05827120875573275,-0.005775219754398246,0.049433646235514356,-0.024571485951532263,0.11106113058641706,0.007479620053186032,0.047319248183064856,0.02728980047160238,-0.015755238520306098,-0.019402062379085996,0.021099985227671914,0.07537182760183642,0.007733824099879121,0.05826984716587052,-0.04569815753581898,-0.019714719991769717,-0.02457069453468659,0.025417672815507508,0.1324794655641785,0.030722787359366358,0.114656331008662,-5.421010862427522e-20,2.168404344971009e-19,0.11435751893042073,-0.0019095043840370793,-0.015984195938783547,-1.3552527156068805e-19,0.11532630106109037,-0.0015788111868760045,-0.013216009123799648,-8.131516293641283e-20,0.0030288559640249285,0.11416734013586552,0.007479561744448294,0.04731818023819938,2.710505431213761e-19,0.031510236123437264,-0.019401803177447417,0.07536891673016007,0.007733388654650532,0.05826628740943553,0.039920694240863634,-0.029715347186684976,-0.02456916200477895,0.021098910999756488,0.11105389349276677,0.007733388654650532,0.05826628740943553,-0.03992069424086363,-0.02971534718668497,-0.02456916200477895,0.021098910999756484,0.025414685189261044,0.5057601202283039,0.11840556176280342,0.47352872944563656,-0.010504615786165747,-0.10480601144886825,0.49384849344395626,-0.006064658148156859,-0.06050793710573233,0.02468508572569328,0.4653428764055026,-0.005014364045944412,-0.05002900689620249,0.020410054995695127,0.011783392068178878,0.46083408129083564,0.02888050944635944,0.19861464510963245,-0.03416217780215647,0.1330310968961726,-0.07945710726340403,0.32167365101088186,0.028879119021694842,0.19860745633291793,0.09812625246194209,-0.09609549866654718,-0.07945341711256677,0.0753718276018364,0.32166684797887407,0.03059901569368727,0.3117911227302078,-0.27895669551142077,-0.1610508209776,-0.13315959886796577,0.11106113058641712,0.11105389349276676,0.7746059439198978]"), gn = "8-fold symmetry: pair(i,j)=i*(i+1)/2+j, idx(P,Q)=P*(P+1)/2+Q", pn = {
        software: "PySCF",
        version: "2.11.0",
        energy: -55.45436165848797
    };
    var bn = {
        format_version: nn,
        system_id: rn,
        label: on,
        description: sn,
        geometry: an,
        basis_id: cn,
        nbf: ln,
        nelec: un,
        e_nuc: dn,
        s_matrix: fn,
        h_core: _n,
        eri_compressed: mn,
        eri_indexing: gn,
        reference: pn
    };
    const Ye = {
        h2_sto3g_r1_4: We,
        "h2_sto3g_r1.4": We,
        heh_plus_sto3g: Mt,
        lih_sto3g: Vt,
        h2o_sto3g: tn,
        nh3_sto3g: bn
    }, ie = new Map;
    function yn(t, e) {
        const n = {
            format_version: e.formatVersion,
            system_id: t,
            label: e.label,
            description: e.description,
            geometry: e.geometry,
            basis_id: e.basisId,
            nbf: e.nbf,
            nelec: e.nelec,
            e_nuc: e.eNuc,
            s_matrix: e.sMatrix,
            h_core: e.hCore,
            eri_compressed: e.eriCompressed,
            eri_indexing: e.eriIndexing
        };
        ie.set(t, n);
    }
    function hn(t) {
        const e = ie.get(t);
        return e || Ye[t];
    }
    function An() {
        const t = Object.keys(Ye), e = Array.from(ie.keys());
        return [
            ...t,
            ...e
        ];
    }
    function wn() {
        return ie.size;
    }
    let me = null;
    function In(t) {
        me = t;
    }
    function Rn(t, e, n) {
        const { requestId: r, systemId: o, options: i } = t;
        if (!me) return {
            type: "error",
            requestId: r,
            code: "WORKER_NOT_READY",
            message: "SCF WASM function not initialized"
        };
        const a = hn(o);
        if (!a) {
            const g = An(), d = wn(), w = d > 0 ? `${g.slice(0, 10).join(", ")}${g.length > 10 ? `, ... (${g.length} total, ${d} custom)` : ""}` : "h2_sto3g_r1.4, heh_plus_sto3g, lih_sto3g, h2o_sto3g, nh3_sto3g";
            return {
                type: "error",
                requestId: r,
                code: "INVALID_PARAMS",
                message: `Unknown system: ${o}. Available systems: ${w}`
            };
        }
        if (n()) return {
            energy: 0,
            converged: !1,
            iterations: 0,
            aborted: !0,
            history: []
        };
        const c = {
            convergenceProfile: i.convergenceProfile,
            maxIterations: i.maxIterations,
            useDiis: i.useDiis,
            diisSize: i.diisSize,
            includeMatrices: i.includeMatrices ?? !1,
            damp: i.damp,
            levelShift: i.levelShift
        };
        let s;
        try {
            s = me(JSON.stringify(a), c);
        } catch (g) {
            return {
                type: "error",
                requestId: r,
                code: "HANDLER_ERROR",
                message: g instanceof Error ? g.message : "SCF computation failed"
            };
        }
        const f = [];
        for(let g = 0; g < s.trace.length; g++){
            const d = s.trace[g];
            if (n()) return {
                energy: d.energy,
                converged: !1,
                iterations: g + 1,
                aborted: !0,
                history: f
            };
            const w = {
                iteration: d.iteration,
                energy: d.energy,
                delta: d.deltaE ?? 0
            };
            d.rmsDensityChange !== null && d.rmsDensityChange !== void 0 && (w.diisError = d.rmsDensityChange), f.push(w);
            const b = g === s.trace.length - 1 && s.converged;
            e({
                module: "scf",
                iteration: d.iteration,
                energy: d.energy,
                delta: d.deltaE ?? 0,
                diisError: d.rmsDensityChange ?? void 0,
                converged: b,
                current: g + 1,
                total: s.iterations,
                message: b ? `Converged after ${g + 1} iterations` : `Iteration ${g + 1}/${s.iterations}: E = ${d.energy.toFixed(10)} Ha`
            });
        }
        const m = {
            energy: s.energy,
            converged: s.converged,
            iterations: s.iterations,
            aborted: !1,
            history: f
        };
        return s.matrices && (m.matrices = {
            nbf: s.matrices.nbf,
            sMatrix: s.matrices.sMatrix,
            hCore: s.matrices.hCore,
            fockMatrix: s.matrices.fockMatrix,
            densityMatrix: s.matrices.densityMatrix,
            moCoefficients: s.matrices.moCoefficients
        }), s.orbitalEnergies && (m.orbitalEnergies = {
            energies: s.orbitalEnergies.energies,
            nOccupied: s.orbitalEnergies.nOccupied
        }), m;
    }
    let K = null, ne = null, re = null;
    function Oe(t) {
        K = t;
    }
    function Sn(t) {
        ne = t;
    }
    function Mn(t) {
        re = t;
    }
    const vn = [
        "H",
        "He",
        "Li",
        "Be",
        "B",
        "C",
        "N",
        "O",
        "F",
        "Ne",
        "Na",
        "Mg",
        "Al",
        "Si",
        "P",
        "S",
        "Cl",
        "Ar"
    ], Te = [
        "sto-3g",
        "3-21g",
        "6-31g",
        "6-31g*",
        "6-31+g*",
        "6-31++g**",
        "cc-pvdz"
    ];
    function En(t) {
        if (!t.atoms || t.atoms.length === 0) return "Geometry must have at least 1 atom.";
        for(let e = 0; e < t.atoms.length; e++){
            const n = t.atoms[e];
            if (!vn.includes(n.symbol)) return `Unsupported element '${n.symbol}' at position ${e}. Only H-Ar are supported.`;
            if (!Array.isArray(n.xyz) || n.xyz.length !== 3) return `Invalid coordinates for atom ${e} (${n.symbol}). Expected [x, y, z] array.`;
            for(let r = 0; r < 3; r++)if (typeof n.xyz[r] != "number" || !Number.isFinite(n.xyz[r])) return `Invalid coordinate value for atom ${e} (${n.symbol}) at index ${r}.`;
        }
        return t.units !== "bohr" && t.units !== "angstrom" ? `Invalid units '${t.units}'. Must be 'bohr' or 'angstrom'.` : null;
    }
    function Dn(t) {
        return Te.includes(t) ? null : `Unknown basis set '${t}'. Supported: ${Te.join(", ")}`;
    }
    function Nn(t, e, n) {
        const { requestId: r, geometry: o, basisSet: i } = t, a = t.useSpherical ?? !0, c = re !== null, s = ne !== null, f = K !== null;
        if (a && !c && !s) return {
            type: "error",
            requestId: r,
            code: "WORKER_NOT_READY",
            message: "Spherical harmonics require compute_integrals_with_options (not available)"
        };
        if (!c && !s && !f) return {
            type: "error",
            requestId: r,
            code: "WORKER_NOT_READY",
            message: "Integral computation WASM function not initialized"
        };
        const m = En(o);
        if (m) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: m
        };
        const g = Dn(i);
        if (g) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: g
        };
        if (n()) return {
            type: "error",
            requestId: r,
            code: "COMPUTATION_CANCELLED",
            message: "Computation cancelled before starting"
        };
        let d = "overlap";
        const w = (b)=>{
            if (n()) return;
            const A = b.phase;
            d = A, e({
                module: "integral",
                phase: A,
                current: b.current,
                total: b.total,
                overallPercent: b.overallPercent,
                message: b.message
            });
        };
        let p;
        try {
            const b = JSON.stringify(o), A = {
                useSpherical: a
            };
            if (re) p = re(b, i, A, w);
            else if (!a && K) p = K(b, i, w);
            else if (ne) p = ne(b, i, A);
            else if (K) p = K(b, i, w);
            else throw new Error("No WASM integral function available");
        } catch (b) {
            return {
                type: "error",
                requestId: r,
                code: "HANDLER_ERROR",
                message: b instanceof Error ? b.message : "Integral computation failed"
            };
        }
        return n() ? {
            type: "error",
            requestId: r,
            code: "COMPUTATION_CANCELLED",
            message: `Computation cancelled during ${d} phase`
        } : {
            formatVersion: p.formatVersion,
            systemId: p.systemId,
            label: p.label,
            description: p.description,
            geometry: {
                atoms: p.geometry.atoms,
                units: p.geometry.units
            },
            basisId: p.basisId,
            nbf: p.nbf,
            nelec: p.nelec,
            eNuc: p.eNuc,
            sMatrix: p.sMatrix,
            hCore: p.hCore,
            eriCompressed: p.eriCompressed,
            eriIndexing: p.eriIndexing,
            metadata: {
                wasmVersion: p.metadata.wasmVersion,
                computeTimeMs: p.metadata.computeTimeMs,
                shellPairs: p.metadata.shellPairs,
                shellQuartets: p.metadata.shellQuartets,
                significantEris: p.metadata.significantEris,
                basisType: p.metadata.basisType || "cartesian"
            }
        };
    }
    let ge = null;
    function $n(t) {
        ge = t;
    }
    function xn(t, e, n) {
        const { requestId: r, atomAZ: o, atomBZ: i, rMin: a, rMax: c, nPoints: s, basisName: f, options: m, useSeeding: g } = t;
        if (!ge) return {
            type: "error",
            requestId: r,
            code: "WORKER_NOT_READY",
            message: "PES scan WASM function not initialized"
        };
        if (o < 1 || o > 10) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `atomAZ must be 1-10, got ${o}`
        };
        if (i < 1 || i > 10) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `atomBZ must be 1-10, got ${i}`
        };
        if (s < 1) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `nPoints must be >= 1, got ${s}`
        };
        if (s > 1 && a >= c) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `rMin (${a}) must be < rMax (${c})`
        };
        if (n()) return {
            points: [],
            equilibrium: null,
            compute_time_ms: 0,
            total_iterations: 0
        };
        const d = {
            atomAZ: o,
            atomBZ: i,
            rMin: a,
            rMax: c,
            nPoints: s,
            basisName: f,
            options: {
                convergenceProfile: m.convergenceProfile,
                maxIterations: m.maxIterations,
                useDiis: m.useDiis,
                diisSize: m.diisSize,
                damp: m.damp,
                includeMatrices: !1
            },
            useSeeding: g ?? !0
        };
        let w = !1;
        const p = [], b = (y)=>n() ? (w = !0, !1) : (p.push({
                r: y.r,
                energy: y.energy,
                converged: y.converged,
                iterations: 0
            }), e({
                module: "pes",
                pointIndex: y.pointIndex,
                totalPoints: y.totalPoints,
                r: y.r,
                energy: y.energy,
                converged: y.converged,
                current: y.pointIndex + 1,
                total: y.totalPoints,
                message: y.converged ? `Point ${y.pointIndex + 1}/${y.totalPoints}: r=${y.r.toFixed(3)} E=${y.energy.toFixed(8)} Ha` : `Point ${y.pointIndex + 1}/${y.totalPoints}: r=${y.r.toFixed(3)} (not converged)`
            }), !0);
        let A;
        try {
            A = ge(d, b);
        } catch (y) {
            return w && p.length > 0 ? {
                points: p,
                equilibrium: null,
                compute_time_ms: 0,
                total_iterations: 0
            } : {
                type: "error",
                requestId: r,
                code: "HANDLER_ERROR",
                message: y instanceof Error ? y.message : "PES scan computation failed"
            };
        }
        return w ? {
            points: A.points,
            equilibrium: null,
            compute_time_ms: A.compute_time_ms,
            total_iterations: A.total_iterations
        } : {
            points: A.points,
            equilibrium: A.equilibrium,
            compute_time_ms: A.compute_time_ms,
            total_iterations: A.total_iterations
        };
    }
    let pe = null;
    function Pn(t) {
        pe = t;
    }
    const Wn = {
        bond: 2,
        angle: 3,
        dihedral: 4
    };
    function On(t, e, n) {
        const { requestId: r, atoms: o, basisName: i, method: a, coordinateType: c, atomIndices: s, scanMode: f, valueMin: m, valueMax: g, nPoints: d, useSeeding: w, useSpherical: p, convergenceProfile: b, maxScfIterations: A, optMaxSteps: y, optGradThreshold: O } = t;
        if (!pe) return {
            type: "error",
            requestId: r,
            code: "NOT_IMPLEMENTED",
            message: "pes_scan_internal WASM function not available (rebuild WASM module)"
        };
        if (!o || o.length === 0) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: "atoms array is empty"
        };
        const F = [
            "rhf",
            "hf",
            "lda",
            "b3lyp",
            "b3lyp-d3bj"
        ];
        if (!F.includes(a.toLowerCase())) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `Invalid method '${a}', expected one of: ${F.join(", ")}`
        };
        const C = [
            "bond",
            "angle",
            "dihedral"
        ];
        if (!C.includes(c)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `Invalid coordinateType '${c}', expected one of: ${C.join(", ")}`
        };
        const N = Wn[c];
        if (s.length !== N) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `coordinateType '${c}' requires ${N} atom indices, got ${s.length}`
        };
        const V = [
            "rigid",
            "relaxed"
        ];
        if (!V.includes(f)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `Invalid scanMode '${f}', expected one of: ${V.join(", ")}`
        };
        if (d < 2) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `nPoints must be >= 2, got ${d}`
        };
        if (m >= g) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `valueMin (${m}) must be < valueMax (${g})`
        };
        if (n()) return {
            coordinate_type: c,
            atom_indices: s,
            points: [],
            equilibrium: null,
            total_iterations: 0,
            scan_mode: f,
            total_opt_steps: 0
        };
        const W = {
            atoms: o,
            basisName: i,
            method: a.toLowerCase(),
            coordinateType: c,
            atomIndices: s,
            scanMode: f,
            valueMin: m,
            valueMax: g,
            nPoints: d,
            useSeeding: w ?? !0,
            useSpherical: p ?? !0,
            convergenceProfile: b ?? "tight"
        };
        A !== void 0 && (W.maxScfIterations = A), y !== void 0 && (W.optMaxSteps = y), O !== void 0 && (W.optGradThreshold = O);
        let B = !1;
        const $ = (M)=>{
            if (n()) {
                B = !0;
                return;
            }
            e({
                module: "pes_internal",
                pointIndex: M.pointIndex,
                totalPoints: M.totalPoints,
                coordinateValue: M.coordinateValue,
                energy: M.energy,
                converged: M.converged,
                optSteps: M.optSteps,
                current: M.pointIndex + 1,
                total: M.totalPoints,
                message: M.converged ? `Point ${M.pointIndex + 1}/${M.totalPoints}: E = ${M.energy.toFixed(8)} Ha` : `Point ${M.pointIndex + 1}/${M.totalPoints}: (not converged)`
            });
        };
        let H;
        const Je = performance.now();
        try {
            H = pe(W, $);
        } catch (M) {
            return {
                type: "error",
                requestId: r,
                code: "HANDLER_ERROR",
                message: M instanceof Error ? M.message : "Internal coordinate PES scan failed"
            };
        }
        const Ze = performance.now() - Je;
        return H.compute_time_ms = Ze, B ? {
            ...H,
            equilibrium: null
        } : H;
    }
    let be = null;
    function Tn(t) {
        be = t;
    }
    const Ln = 4, j = new Map;
    let kn = 1;
    function Fn(t) {
        return t instanceof Float64Array ? t.byteLength === t.buffer.byteLength && t.byteOffset === 0 ? t : new Float64Array(t) : Float64Array.from(t);
    }
    function Cn(t) {
        for(j.set(t.gridId, t); j.size > Ln;){
            const e = j.keys().next();
            if (e.done) break;
            j.delete(e.value);
        }
    }
    function Vn(t) {
        const e = j.get(t);
        if (e !== void 0) return j.delete(t), j.set(t, e), e;
    }
    function Hn(t, e, n, r) {
        const o = kn++;
        return Cn({
            gridId: o,
            values: Fn(t),
            gridDims: e,
            gridOrigin: n,
            gridSpacing: r
        }), o;
    }
    function zn(t) {
        const { requestId: e, moCoefficients: n, atoms: r, basisName: o, gridOrigin: i, gridSpacing: a, gridDims: c, useSpherical: s } = t;
        if (!be) return {
            type: "error",
            requestId: e,
            code: "WORKER_NOT_READY",
            message: "MO grid evaluation WASM function not initialized"
        };
        if (!n || n.length === 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "moCoefficients must be a non-empty array"
        };
        if (!r || r.length === 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "atoms must be a non-empty array"
        };
        if (a <= 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridSpacing must be positive, got ${a}`
        };
        if (c.some((m)=>m < 2)) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridDims must all be >= 2, got [${c.join(", ")}]`
        };
        const f = {
            moCoefficients: n,
            atoms: r,
            basisName: o,
            gridOrigin: i,
            gridSpacing: a,
            gridDims: c
        };
        f.useSpherical = s ?? !0;
        try {
            const m = be(f);
            return {
                gridId: Hn(m.values, m.gridDims, m.gridOrigin, m.gridSpacing),
                gridOrigin: m.gridOrigin,
                gridSpacing: m.gridSpacing,
                gridDims: m.gridDims,
                maxAbsValue: m.maxAbsValue,
                normSqIntegral: m.normSqIntegral,
                computeTimeMs: m.computeTimeMs
            };
        } catch (m) {
            return {
                type: "error",
                requestId: e,
                code: "HANDLER_ERROR",
                message: m instanceof Error ? m.message : "MO grid evaluation failed"
            };
        }
    }
    let ye = null, he = null, oe = null;
    function jn(t) {
        ye = t;
    }
    function Bn(t) {
        he = t;
    }
    function Kn(t) {
        oe = t;
    }
    function Un(t) {
        const e = new Set;
        for (const n of [
            t.positive,
            t.negative
        ])if (n) for (const r of [
            n.vertices,
            n.indices,
            n.normals
        ]){
            if (!ArrayBuffer.isView(r)) continue;
            const o = r.buffer;
            o instanceof ArrayBuffer && (r.byteOffset !== 0 || r.byteLength !== o.byteLength || e.add(o));
        }
        return [
            ...e
        ];
    }
    function Gn(t) {
        const { requestId: e, gridData: n, gridDims: r, gridOrigin: o, gridSpacing: i, isovalue: a } = t;
        if (!ye) return {
            type: "error",
            requestId: e,
            code: "WORKER_NOT_READY",
            message: "Marching cubes WASM function not initialized"
        };
        if (!n || n.length === 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "gridData must be a non-empty array"
        };
        if (r.some((f)=>f < 2)) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridDims must all be >= 2, got [${r.join(", ")}]`
        };
        const c = r[0] * r[1] * r[2];
        if (n.length !== c) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridData length ${n.length} does not match dims [${r.join(", ")}] = ${c}`
        };
        if (i <= 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridSpacing must be positive, got ${i}`
        };
        const s = {
            gridData: n,
            gridDims: r,
            gridOrigin: o,
            gridSpacing: i,
            isovalue: a
        };
        try {
            return ye(s);
        } catch (f) {
            return {
                type: "error",
                requestId: e,
                code: "HANDLER_ERROR",
                message: f instanceof Error ? f.message : "Marching cubes extraction failed"
            };
        }
    }
    function Yn(t) {
        const { requestId: e, gridId: n, gridData: r, isovalue: o } = t;
        if (!oe && !he) return {
            type: "error",
            requestId: e,
            code: "WORKER_NOT_READY",
            message: "Dual marching cubes WASM function not initialized"
        };
        const i = n !== void 0, a = r != null;
        if (i && a) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "exactly one of gridId or gridData must be provided, got both"
        };
        if (!i && !a) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "exactly one of gridId or gridData must be provided, got neither"
        };
        let c, s, f, m;
        if (i) {
            const d = Vn(n);
            if (!d) return {
                type: "error",
                requestId: e,
                code: "GRID_NOT_CACHED",
                message: `grid ${n} is no longer cached in the worker; recompute the grid and retry`
            };
            c = d.values, s = d.gridDims, f = d.gridOrigin, m = d.gridSpacing;
        } else {
            if (c = r, c.length === 0) return {
                type: "error",
                requestId: e,
                code: "INVALID_PARAMS",
                message: "gridData must be a non-empty array"
            };
            s = t.gridDims, f = t.gridOrigin, m = t.gridSpacing;
        }
        if (s.some((d)=>d < 2)) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridDims must all be >= 2, got [${s.join(", ")}]`
        };
        if (m <= 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridSpacing must be positive, got ${m}`
        };
        const g = s[0] * s[1] * s[2];
        if (c.length !== g) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `grid length ${c.length} does not match dims [${s.join(", ")}] = ${g}`
        };
        try {
            if (oe) return oe(Array.isArray(c) ? Float64Array.from(c) : c, s[0], s[1], s[2], f[0], f[1], f[2], m, o);
            const d = {
                gridData: Array.isArray(c) ? c : Array.from(c),
                gridDims: s,
                gridOrigin: f,
                gridSpacing: m,
                isovalue: o
            };
            return he(d);
        } catch (d) {
            return {
                type: "error",
                requestId: e,
                code: "HANDLER_ERROR",
                message: d instanceof Error ? d.message : "Dual marching cubes extraction failed"
            };
        }
    }
    let Ae = null;
    function Qn(t) {
        Ae = t;
    }
    function qn(t) {
        if (!Ae) return {
            type: "error",
            requestId: t.requestId,
            code: "WORKER_NOT_READY",
            message: "WASM get_basis_info function not available. Rebuild WASM?"
        };
        try {
            return Ae(t.atomicNumber, t.basisName);
        } catch (e) {
            const n = e instanceof Error ? e.message : "Unknown error in get_basis_info";
            return {
                type: "error",
                requestId: t.requestId,
                code: "HANDLER_ERROR",
                message: n
            };
        }
    }
    let we = null;
    function Jn(t) {
        we = t;
    }
    function Zn(t) {
        if (!we) return {
            type: "error",
            requestId: t.requestId,
            code: "WORKER_NOT_READY",
            message: "WASM evaluate_radial_profile function not available. Rebuild WASM?"
        };
        try {
            const e = {
                atomicNumber: t.atomicNumber,
                basisName: t.basisName,
                shellIndex: t.shellIndex
            };
            return t.nPoints !== void 0 && (e.nPoints = t.nPoints), t.rMax !== void 0 && (e.rMax = t.rMax), we(e);
        } catch (e) {
            const n = e instanceof Error ? e.message : "Unknown error in evaluate_radial_profile";
            return {
                type: "error",
                requestId: t.requestId,
                code: "HANDLER_ERROR",
                message: n
            };
        }
    }
    let Ie = null;
    function Xn(t) {
        Ie = t;
    }
    function er(t) {
        if (!Ie) return {
            type: "error",
            requestId: t.requestId,
            code: "WORKER_NOT_READY",
            message: "WASM overlap_vs_distance function not available. Rebuild WASM?"
        };
        try {
            const e = {
                elementA: t.elementA,
                basisA: t.basisA,
                shellIndexA: t.shellIndexA,
                elementB: t.elementB,
                basisB: t.basisB,
                shellIndexB: t.shellIndexB,
                rMin: t.rMin,
                rMax: t.rMax,
                nPoints: t.nPoints
            };
            return Ie(e);
        } catch (e) {
            const n = e instanceof Error ? e.message : "Unknown error in overlap_vs_distance";
            return {
                type: "error",
                requestId: t.requestId,
                code: "HANDLER_ERROR",
                message: n
            };
        }
    }
    let Re = null;
    function tr(t) {
        Re = t;
    }
    function nr(t) {
        if (!Re) return {
            type: "error",
            requestId: t.requestId,
            code: "WORKER_NOT_READY",
            message: "WASM compute_integral_matrices function not available. Rebuild WASM?"
        };
        try {
            const e = {
                atoms: t.geometry.atoms,
                basisName: t.basisName,
                units: t.geometry.units
            };
            return e.useSpherical = t.useSpherical ?? !0, Re(e);
        } catch (e) {
            const n = e instanceof Error ? e.message : "Unknown error in compute_integral_matrices";
            return {
                type: "error",
                requestId: t.requestId,
                code: "HANDLER_ERROR",
                message: n
            };
        }
    }
    let Se = null;
    function rr(t) {
        Se = t;
    }
    function or(t) {
        if (!Se) return {
            type: "error",
            requestId: t.requestId,
            code: "WORKER_NOT_READY",
            message: "WASM integral_with_breakdown function not available. Rebuild WASM?"
        };
        try {
            const e = {
                atoms: t.geometry.atoms,
                basisName: t.basisName,
                units: t.geometry.units,
                integralType: t.integralType,
                indices: t.indices
            };
            return Se(e);
        } catch (e) {
            const n = e instanceof Error ? e.message : "Unknown error in integral_with_breakdown";
            return {
                type: "error",
                requestId: t.requestId,
                code: "HANDLER_ERROR",
                message: n
            };
        }
    }
    let Me = null;
    function ir(t) {
        Me = t;
    }
    function sr(t) {
        if (!Me) return {
            type: "error",
            requestId: t.requestId,
            code: "WORKER_NOT_READY",
            message: "WASM fock_decomposition function not available. Rebuild WASM?"
        };
        try {
            const e = {
                atoms: t.geometry.atoms,
                basisName: t.basisSet,
                units: t.geometry.units,
                densityMatrix: t.densityMatrix
            };
            return Me(e);
        } catch (e) {
            const n = e instanceof Error ? e.message : "Unknown error in fock_decomposition";
            return {
                type: "error",
                requestId: t.requestId,
                code: "HANDLER_ERROR",
                message: n
            };
        }
    }
    let ve = null;
    function ar(t) {
        ve = t;
    }
    function cr(t) {
        if (!ve) return {
            type: "error",
            requestId: t.requestId,
            code: "WORKER_NOT_READY",
            message: "WASM eri_detail function not available. Rebuild WASM?"
        };
        try {
            const e = {
                atoms: t.geometry.atoms,
                basisName: t.basisName,
                units: t.geometry.units,
                indices: t.indices
            };
            return ve(e);
        } catch (e) {
            const n = e instanceof Error ? e.message : "Unknown error in eri_detail";
            return {
                type: "error",
                requestId: t.requestId,
                code: "HANDLER_ERROR",
                message: n
            };
        }
    }
    let Ee = null;
    function lr(t) {
        Ee = t;
    }
    let ae = null, Le = null;
    function ur(t) {
        const e = t.densityMatrix.length, n = e > 0 ? t.densityMatrix[0] : 0, r = e > 0 ? t.densityMatrix[e - 1] : 0;
        let o = 0;
        for(let i = 0; i < e; i++)o += t.densityMatrix[i];
        return `${e}:${n}:${r}:${o}:${t.gridDims.join(",")}:${t.gridSpacing}:${t.gridOrigin.join(",")}:${t.basisName}:${t.useSpherical ?? !0}`;
    }
    function dr(t) {
        const { requestId: e, densityMatrix: n, atoms: r, basisName: o, gridOrigin: i, gridSpacing: a, gridDims: c, nElectrons: s, useSpherical: f } = t;
        if (!Ee) return {
            type: "error",
            requestId: e,
            code: "WORKER_NOT_READY",
            message: "Density grid evaluation WASM function not initialized"
        };
        if (!n || n.length === 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "densityMatrix must be a non-empty array"
        };
        if (!r || r.length === 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "atoms must be a non-empty array"
        };
        if (a <= 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridSpacing must be positive, got ${a}`
        };
        if (c.some((d)=>d < 2)) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridDims must all be >= 2, got [${c.join(", ")}]`
        };
        if (s < 1) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `nElectrons must be >= 1, got ${s}`
        };
        const m = ur(t);
        if (Le === m && ae) return ae;
        const g = {
            densityMatrix: n,
            atoms: r,
            basisName: o,
            gridOrigin: i,
            gridSpacing: a,
            gridDims: c,
            nElectrons: s
        };
        g.useSpherical = f ?? !0;
        try {
            const d = Ee(g);
            return Le = m, ae = d, d;
        } catch (d) {
            return {
                type: "error",
                requestId: e,
                code: "HANDLER_ERROR",
                message: d instanceof Error ? d.message : "Density grid evaluation failed"
            };
        }
    }
    let De = null;
    function fr(t) {
        De = t;
    }
    function _r(t) {
        const { requestId: e, totalDensity: n, atoms: r, gridOrigin: o, gridSpacing: i, gridDims: a } = t;
        if (!De) return {
            type: "error",
            requestId: e,
            code: "WORKER_NOT_READY",
            message: "Difference density WASM function not initialized. Rebuild WASM?"
        };
        if (!n || n.length === 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "totalDensity must be a non-empty array"
        };
        if (!r || r.length === 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: "atoms must be a non-empty array"
        };
        if (i <= 0) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridSpacing must be positive, got ${i}`
        };
        if (a.some((f)=>f < 2)) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `gridDims must all be >= 2, got [${a.join(", ")}]`
        };
        const c = a[0] * a[1] * a[2];
        if (n.length !== c) return {
            type: "error",
            requestId: e,
            code: "INVALID_PARAMS",
            message: `totalDensity length (${n.length}) does not match gridDims product (${c})`
        };
        const s = {
            totalDensity: n,
            atoms: r,
            gridOrigin: o,
            gridSpacing: i,
            gridDims: a
        };
        try {
            return De(s);
        } catch (f) {
            return {
                type: "error",
                requestId: e,
                code: "HANDLER_ERROR",
                message: f instanceof Error ? f.message : "Difference density evaluation failed"
            };
        }
    }
    let Ne = null;
    function mr(t) {
        Ne = t;
    }
    function gr(t, e, n) {
        const { requestId: r, atoms: o, basisName: i, method: a, maxSteps: c, gradThreshold: s, energyThreshold: f, convergenceSet: m } = t;
        if (!Ne) return {
            type: "error",
            requestId: r,
            code: "NOT_IMPLEMENTED",
            message: "optimize_geometry WASM function not available (rebuild WASM module)"
        };
        if (!o || o.length === 0) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: "atoms array is empty"
        };
        if (![
            "rhf",
            "hf",
            "lda",
            "b3lyp",
            "b3lyp-d3bj"
        ].includes(a.toLowerCase())) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `Invalid method '${a}', expected one of: rhf, lda, b3lyp, b3lyp-d3bj`
        };
        if (n()) return {
            converged: !1,
            steps: [],
            finalEnergy: 0,
            finalGeometry: [],
            totalSteps: 0,
            computeTimeMs: 0
        };
        const d = {
            atoms: o,
            basisName: i,
            method: a.toLowerCase(),
            maxSteps: c ?? 50,
            memorySize: 7
        };
        m !== void 0 ? (d.convergenceSet = m, s !== void 0 && (d.gradThreshold = s), f !== void 0 && (d.energyThreshold = f)) : (d.gradThreshold = s ?? 45e-5, d.energyThreshold = f ?? 1e-6);
        let w = !1;
        const p = (b)=>{
            if (n()) {
                w = !0;
                return;
            }
            e({
                module: "optimization",
                step: b.step,
                energy: b.energy,
                maxGradient: b.maxGradient,
                rmsGradient: b.rmsGradient,
                current: b.step,
                total: 0,
                message: `Step ${b.step}: E=${b.energy.toFixed(8)} Ha, max|g|=${b.maxGradient.toExponential(2)}`
            });
        };
        try {
            const b = Ne(d, p, t.cancelFlag ?? null);
            return w ? {
                ...b,
                converged: !1
            } : b;
        } catch (b) {
            const A = b instanceof Error ? b.message : "Geometry optimization failed";
            return A.toLowerCase().startsWith("cancelled") ? {
                type: "error",
                requestId: r,
                code: "COMPUTATION_CANCELLED",
                message: A
            } : {
                type: "error",
                requestId: r,
                code: "HANDLER_ERROR",
                message: A
            };
        }
    }
    let $e = null;
    function pr(t) {
        $e = t;
    }
    function br(t) {
        const { requestId: e } = t;
        if (!$e) return {
            type: "error",
            requestId: e,
            code: "WORKER_NOT_READY",
            message: "Population analysis WASM function not initialized"
        };
        try {
            const n = {
                densityMatrix: t.densityMatrix,
                overlapMatrix: t.overlapMatrix,
                nbf: t.nbf,
                atoms: t.atoms
            };
            return $e(n);
        } catch (n) {
            return {
                type: "error",
                requestId: e,
                code: "HANDLER_ERROR",
                message: n instanceof Error ? n.message : "Population analysis failed"
            };
        }
    }
    let xe = null;
    function ke(t) {
        xe = t;
    }
    const Fe = [
        "rhf",
        "hf",
        "lda",
        "b3lyp",
        "b3lyp-d3bj"
    ], Ce = [
        "lorentzian",
        "gaussian"
    ], Ve = [
        "loose",
        "medium",
        "tight"
    ];
    function yr(t, e, n) {
        const { requestId: r, atoms: o, basisName: i, method: a, temperatureK: c, pressurePa: s, symmetryNumberOverride: f, multiplicity: m, broadeningKind: g, fwhmCm1: d, convergenceProfile: w, maxIterations: p, useSpherical: b } = t;
        if (!xe) return {
            type: "error",
            requestId: r,
            code: "NOT_IMPLEMENTED",
            message: "compute_frequencies WASM function not available (rebuild WASM module)"
        };
        if (!o || o.length === 0) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: "FrequencyRequest: atoms array must not be empty"
        };
        if (!i || i.trim() === "") return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: "FrequencyRequest: basisName is required"
        };
        const A = a.toLowerCase();
        if (!Fe.includes(A)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: method must be one of ${Fe.join(", ")}, got '${a}'`
        };
        if (c !== void 0 && !(Number.isFinite(c) && c > 0)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: temperatureK must be positive and finite, got ${c}`
        };
        if (s !== void 0 && !(Number.isFinite(s) && s > 0)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: pressurePa must be positive and finite, got ${s}`
        };
        if (d !== void 0 && !(Number.isFinite(d) && d > 0)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: fwhmCm1 must be positive and finite, got ${d}`
        };
        if (m !== void 0 && !(Number.isInteger(m) && m >= 1)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: multiplicity must be an integer >= 1, got ${m}`
        };
        if (f !== void 0 && !(Number.isInteger(f) && f >= 1)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: symmetryNumberOverride must be an integer >= 1, got ${f}`
        };
        if (g !== void 0 && !Ce.includes(g)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: broadeningKind must be one of ${Ce.join(", ")}, got '${g}'`
        };
        if (w !== void 0 && !Ve.includes(w)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: convergenceProfile must be one of ${Ve.join(", ")}, got '${w}'`
        };
        if (p !== void 0 && !(Number.isInteger(p) && p >= 1)) return {
            type: "error",
            requestId: r,
            code: "INVALID_PARAMS",
            message: `FrequencyRequest: maxIterations must be a positive integer, got ${p}`
        };
        if (n()) return hr(o.length);
        const y = {
            atoms: o,
            basisName: i,
            method: A
        };
        c !== void 0 && (y.temperatureK = c), s !== void 0 && (y.pressurePa = s), f !== void 0 && (y.symmetryNumberOverride = f), m !== void 0 && (y.multiplicity = m), g !== void 0 && (y.broadeningKind = g), d !== void 0 && (y.fwhmCm1 = d), w !== void 0 && (y.convergenceProfile = w), p !== void 0 && (y.maxIterations = p), y.useSpherical = b ?? !0;
        let O = !1;
        const F = ($)=>{
            if (n()) {
                O = !0;
                return;
            }
            const H = Number.isFinite($.percent) ? $.percent : 0;
            e({
                module: "frequency",
                phase: $.phase,
                percent: H,
                step: $.step ?? "",
                message: $.message ?? "",
                current: Math.round(H * 100),
                total: 100
            });
        }, C = performance.now();
        let N;
        try {
            N = xe(y, F);
        } catch ($) {
            return {
                type: "error",
                requestId: r,
                code: "HANDLER_ERROR",
                message: $ instanceof Error ? $.message : "Frequency analysis failed"
            };
        }
        const V = performance.now() - C;
        if (!N || typeof N != "object") return {
            type: "error",
            requestId: r,
            code: "HANDLER_ERROR",
            message: "compute_frequencies returned an unexpected value"
        };
        const W = N, B = {
            ...W.timingMs,
            totalMs: V
        };
        return {
            ...W,
            timingMs: B,
            aborted: O
        };
    }
    function hr(t) {
        const e = {
            integralsMs: 0,
            nuclearCphfMs: 0,
            fieldCphfMs: 0,
            assemblyMs: 0,
            modesMs: 0,
            totalMs: 0
        }, n = {
            temperatureK: 0,
            pressurePa: 0,
            symmetryNumber: 0,
            symmetryNumberSource: "detected",
            multiplicity: 0,
            totalMassAmu: 0,
            nVibModesUsed: 0,
            nImag: 0,
            zpeHa: 0,
            e0kHa: 0,
            internalEnergyHa: 0,
            enthalpyHa: 0,
            entropyHaPerK: 0,
            gibbsHa: 0,
            cvHaPerK: 0,
            cpHaPerK: 0,
            eTransHa: 0,
            hTransHa: 0,
            sTransHaPerK: 0,
            cvTransHaPerK: 0,
            cpTransHaPerK: 0,
            eRotHa: 0,
            hRotHa: 0,
            sRotHaPerK: 0,
            cvRotHaPerK: 0,
            cpRotHaPerK: 0,
            eVibThermalHa: 0,
            hVibHa: 0,
            sVibHaPerK: 0,
            cvVibHaPerK: 0,
            cpVibHaPerK: 0,
            sElecHaPerK: 0
        }, r = {
            wavenumbersCm1: [],
            intensity: [],
            kind: "lorentzian",
            fwhmCm1: 0
        };
        return {
            nAtoms: t,
            nModes: 0,
            rotorType: "atom",
            electronicEnergyHa: 0,
            dipoleAu: [
                0,
                0,
                0
            ],
            dipoleDebye: [
                0,
                0,
                0
            ],
            polarizabilityAu: [
                [
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    0
                ]
            ],
            polarizabilityAng3: [
                [
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    0
                ]
            ],
            frequenciesCm1: [],
            reducedMassesAmu: [],
            forceConstantsMdyne: [],
            normalModesCartesian: [],
            rotationalConstantsGhz: [
                0,
                0,
                0
            ],
            irIntensitiesKmPerMol: [],
            ramanAvailable: !1,
            ramanActivitiesA4Amu: [],
            depolarizationRatios: [],
            thermochemistry: n,
            irSpectrum: r,
            ramanSpectrum: {
                ...r
            },
            timingMs: e,
            aborted: !0
        };
    }
    let P = {
        status: "pending"
    };
    const R = new Map;
    let Qe = !1, He = !1;
    const Pe = [];
    function u(t, e) {
        if (e && e.length > 0) {
            self.postMessage(t, {
                transfer: e
            });
            return;
        }
        self.postMessage(t);
    }
    function T(t, e, n) {
        return {
            type: "error",
            requestId: t,
            code: e,
            message: n
        };
    }
    function I(t, e) {
        return {
            type: "result",
            requestId: t,
            data: e
        };
    }
    function L(t, e) {
        return {
            type: "progress",
            requestId: t,
            progress: e
        };
    }
    function Ar(t, e) {
        return t.aborted = e(), t;
    }
    const wr = "/wasm-threaded/qc_wasm.js";
    let h = Ge;
    async function Ir() {
        if (globalThis.crossOriginIsolated === !0 && typeof SharedArrayBuffer < "u") try {
            const e = await import(wr).then(async (m)=>{
                await m.__tla;
                return m;
            });
            if (typeof e.initThreadPool == "function") {
                await e.default();
                const n = Math.max(1, navigator.hardwareConcurrency || 1);
                return await e.initThreadPool(n), h = e, console.log(`[Worker] Threaded WASM active: ${n} threads (crossOriginIsolated)`), {
                    threadsAvailable: !0,
                    numThreads: n
                };
            }
            console.warn("[Worker] wasm-threaded artifact has no initThreadPool export — using sequential WASM");
        } catch (e) {
            console.warn("[Worker] Threaded WASM unavailable (artifact missing or thread-pool init failed) — using sequential WASM:", e);
        }
        return await Ue(), h = Ge, {
            threadsAvailable: !1,
            numThreads: 0
        };
    }
    const Rr = "/wasm-spectra-threaded/qc_wasm_spectra.js";
    async function Sr() {
        if (globalThis.crossOriginIsolated === !0 && typeof SharedArrayBuffer < "u") try {
            const n = await import(Rr).then(async (m)=>{
                await m.__tla;
                return m;
            });
            if (typeof n.initThreadPool == "function") {
                await n.default();
                const r = Math.max(1, navigator.hardwareConcurrency || 1);
                await n.initThreadPool(r), ke(n.compute_frequencies), console.info(`[Worker] Threaded spectra WASM active: ${r} threads (crossOriginIsolated)`);
                return;
            }
            console.warn("[Worker] wasm-spectra-threaded artifact has no initThreadPool export — using sequential spectra WASM");
        } catch (n) {
            console.warn("[Worker] Threaded spectra WASM unavailable (artifact missing or thread-pool init failed) — using sequential spectra WASM:", n);
        }
        const e = await import("./qc_wasm_spectra-DqCfyFHZ.js");
        await e.default(), ke(e.compute_frequencies), console.info("[Worker] Sequential spectra WASM active");
    }
    async function Mr() {
        try {
            const t = await Ir(), e = h.version();
            typeof h.boys_eval == "function" && typeof h.boys_eval_many == "function" && typeof h.boys_eval_all == "function" ? B0(h.boys_eval, h.boys_eval_many, h.boys_eval_all) : console.warn("[Worker] Boys WASM exports missing — Boys module will be unavailable. Rebuild WASM?"), typeof h.rys_compute == "function" && typeof h.rys_error_curve == "function" ? Y0(h.rys_compute, h.rys_error_curve) : console.warn("[Worker] Rys WASM exports missing — Rys module will be unavailable. Rebuild WASM?"), In(h.scf_run);
            const n = h.compute_integrals_with_options_and_progress, r = h.compute_integrals_with_progress, o = h.compute_integrals_with_options, i = h.compute_integrals;
            typeof n == "function" && Mn(n), typeof r == "function" ? Oe(r) : typeof i == "function" && Oe(((W, B)=>i(W, B))), typeof o == "function" && Sn(o);
            const a = h.pes_scan;
            typeof a == "function" ? $n(a) : console.warn('[Worker] WASM function "pes_scan" not found — PES scan will be unavailable. Rebuild WASM?');
            const c = h.pes_scan_internal;
            typeof c == "function" ? Pn(c) : console.warn('[Worker] WASM function "pes_scan_internal" not found — internal coordinate PES scan will be unavailable. Rebuild WASM?');
            const s = h.evaluate_mo_grid;
            typeof s == "function" ? Tn(s) : console.warn('[Worker] WASM function "evaluate_mo_grid" not found — orbital visualization will be unavailable. Rebuild WASM?');
            const f = h.marching_cubes;
            typeof f == "function" ? jn(f) : console.warn('[Worker] WASM function "marching_cubes" not found — isosurface extraction will be unavailable. Rebuild WASM?');
            const m = h.dual_marching_cubes;
            typeof m == "function" ? Bn(m) : console.warn('[Worker] WASM function "dual_marching_cubes" not found — dual isosurface extraction will be unavailable. Rebuild WASM?');
            const g = h.dual_marching_cubes_typed;
            typeof g == "function" ? Kn(g) : console.warn('[Worker] WASM function "dual_marching_cubes_typed" not found — falling back to the serde dual_marching_cubes export. Rebuild WASM?');
            const d = h.get_basis_info;
            typeof d == "function" ? Qn(d) : console.warn('[Worker] WASM function "get_basis_info" not found — basis info queries will be unavailable. Rebuild WASM?');
            const w = h.evaluate_radial_profile;
            typeof w == "function" ? Jn(w) : console.warn('[Worker] WASM function "evaluate_radial_profile" not found — radial profile evaluation will be unavailable. Rebuild WASM?');
            const p = h.overlap_vs_distance;
            typeof p == "function" ? Xn(p) : console.warn('[Worker] WASM function "overlap_vs_distance" not found — overlap distance plot will be unavailable. Rebuild WASM?');
            const b = h.compute_integral_matrices;
            typeof b == "function" ? tr(b) : console.warn('[Worker] WASM function "compute_integral_matrices" not found — integral matrices will be unavailable. Rebuild WASM?');
            const A = h.integral_with_breakdown;
            typeof A == "function" ? rr(A) : console.warn('[Worker] WASM function "integral_with_breakdown" not found — primitive breakdown will be unavailable. Rebuild WASM?');
            const y = h.fock_decomposition;
            typeof y == "function" ? ir(y) : console.warn('[Worker] WASM function "fock_decomposition" not found — Fock build tracing will be unavailable. Rebuild WASM?');
            const O = h.eri_detail;
            typeof O == "function" ? ar(O) : console.warn('[Worker] WASM function "eri_detail" not found — ERI browser will be unavailable. Rebuild WASM?');
            const F = h.evaluate_density_grid;
            typeof F == "function" ? lr(F) : console.warn('[Worker] WASM function "evaluate_density_grid" not found — density grid evaluation will be unavailable. Rebuild WASM?');
            const C = h.compute_difference_density;
            typeof C == "function" ? fr(C) : console.warn('[Worker] WASM function "compute_difference_density" not found — difference density will be unavailable. Rebuild WASM?');
            const N = h.optimize_geometry;
            typeof N == "function" ? mr(N) : console.warn('[Worker] WASM function "optimize_geometry" not found — geometry optimization will be unavailable. Rebuild WASM?');
            const V = h.compute_population;
            typeof V == "function" ? pr(V) : console.warn('[Worker] WASM function "compute_population" not found — population analysis will be unavailable. Rebuild WASM?'), P = {
                status: "ready",
                wasmVersion: e,
                threadsAvailable: t.threadsAvailable,
                numThreads: t.numThreads
            };
        } catch (t) {
            const e = t instanceof Error ? t.message : "Unknown initialization error";
            P = {
                status: "error",
                message: e
            }, console.error("[Worker] WASM initialization failed:", e);
        }
        for(Qe = !0; Pe.length > 0;){
            const t = Pe.shift();
            qe(t);
        }
    }
    async function qe(t) {
        const { requestId: e } = t;
        if (t.type === "ping") {
            const n = P.status === "ready" ? P.wasmVersion : "not_initialized", r = P.status === "ready" ? {
                threadsAvailable: P.threadsAvailable,
                numThreads: P.numThreads
            } : {
                threadsAvailable: !1,
                numThreads: 0
            };
            u(j0(t, n, r));
            return;
        }
        if (P.status !== "ready") {
            u(T(e, "WORKER_NOT_READY", P.status === "pending" ? "Worker is still initializing WASM module" : `WASM initialization failed: ${P.message}`));
            return;
        }
        R.delete(e);
        try {
            switch(t.type){
                case "boys_eval":
                    {
                        const n = K0(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "boys_sweep":
                    {
                        const n = U0(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "boys_eval_all":
                    {
                        const n = G0(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "rys_compute":
                    {
                        const n = Q0(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "rys_error_curve":
                    {
                        const n = q0(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "scf_run":
                    {
                        const o = Rn(t, (i)=>{
                            u(L(e, i));
                        }, ()=>R.get(e) === !0);
                        R.delete(e), "code" in o ? u(o) : u(I(e, o));
                        break;
                    }
                case "integral_compute":
                    {
                        const o = Nn(t, (i)=>{
                            u(L(e, i));
                        }, ()=>R.get(e) === !0);
                        R.delete(e), "code" in o ? u(o) : (yn(o.systemId, o), u(I(e, o)));
                        break;
                    }
                case "pes_scan":
                    {
                        const o = xn(t, (i)=>{
                            u(L(e, i));
                        }, ()=>R.get(e) === !0);
                        R.delete(e), "code" in o ? u(o) : u(I(e, o));
                        break;
                    }
                case "pes_scan_internal":
                    {
                        const o = On(t, (i)=>{
                            u(L(e, i));
                        }, ()=>R.get(e) === !0);
                        R.delete(e), "code" in o ? u(o) : u(I(e, o));
                        break;
                    }
                case "mo_grid":
                    {
                        const n = zn(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "marching_cubes":
                    {
                        const n = Gn(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "dual_marching_cubes":
                    {
                        const n = Yn(t);
                        "code" in n ? u(n) : u(I(e, n), Un(n));
                        break;
                    }
                case "basis_info":
                    {
                        const n = qn(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "radial_profile":
                    {
                        const n = Zn(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "overlap_distance":
                    {
                        const n = er(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "integral_matrices":
                    {
                        const n = nr(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "integral_breakdown":
                    {
                        const n = or(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "fock_decomposition":
                    {
                        const n = sr(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "eri_detail":
                    {
                        const n = cr(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "density_grid":
                    {
                        const n = dr(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "difference_density":
                    {
                        const n = _r(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "optimize_geometry":
                    {
                        const o = gr(t, (i)=>{
                            u(L(e, i));
                        }, ()=>R.get(e) === !0);
                        R.delete(e), "code" in o ? u(o) : u(I(e, o));
                        break;
                    }
                case "population_analysis":
                    {
                        const n = br(t);
                        "code" in n ? u(n) : u(I(e, n));
                        break;
                    }
                case "frequency":
                    {
                        const n = (i)=>{
                            u(L(e, i));
                        }, r = ()=>R.get(e) === !0;
                        try {
                            He || (await Sr(), He = !0);
                        } catch (i) {
                            const a = i instanceof Error ? i.message : String(i);
                            u(T(e, "HANDLER_ERROR", `Failed to load spectra WASM module: ${a}`));
                            break;
                        }
                        const o = yr(t, n, r);
                        R.delete(e), "code" in o ? u(o) : u(I(e, o));
                        break;
                    }
                case "ks_scf":
                    {
                        const n = ()=>R.get(e) === !0;
                        try {
                            const r = h.ks_scf;
                            if (!r) {
                                R.delete(e), u(T(e, "NOT_IMPLEMENTED", "ks_scf WASM function not available (rebuild WASM module)"));
                                break;
                            }
                            const o = t.maxIterations ?? 100, i = {
                                atoms: t.atoms,
                                basisName: t.basisName,
                                method: t.method,
                                convergenceProfile: t.convergenceProfile ?? "tight",
                                maxIterations: o,
                                useDiis: t.useDiis ?? !0,
                                gridQuality: t.gridQuality ?? "standard",
                                eriMode: t.eriMode ?? "auto"
                            };
                            t.useSpherical && (i.useSpherical = !0);
                            const a = r(i, (c)=>{
                                const s = c;
                                if (s.phase === "integrals") u(L(e, {
                                    module: "scf_integrals",
                                    step: String(s.step),
                                    percent: Number(s.percent),
                                    message: String(s.message),
                                    current: 0,
                                    total: 100
                                }));
                                else {
                                    const f = s;
                                    u(L(e, {
                                        module: "scf",
                                        iteration: f.iteration,
                                        energy: f.energy,
                                        delta: f.deltaE ?? 0,
                                        diisError: f.rmsDensityChange,
                                        converged: !1,
                                        current: f.iteration,
                                        total: o,
                                        message: `Iteration ${f.iteration}: E = ${f.energy.toFixed(10)} Ha`
                                    }));
                                }
                            }, t.cancelFlag ?? null);
                            Ar(a, n), R.delete(e), u(I(e, a));
                        } catch (r) {
                            R.delete(e);
                            const o = r instanceof Error ? r.message : String(r);
                            o.toLowerCase().startsWith("cancelled") ? u(T(e, "COMPUTATION_CANCELLED", o)) : u(T(e, "HANDLER_ERROR", `KS-SCF error: ${o}`));
                        }
                        break;
                    }
                case "dipole":
                    {
                        const n = h.compute_dipole;
                        if (!n) {
                            u(T(e, "NOT_IMPLEMENTED", "compute_dipole WASM function not available (rebuild WASM module)"));
                            break;
                        }
                        try {
                            const r = {
                                densityMatrix: t.densityMatrix,
                                atoms: t.atoms,
                                basisName: t.basisName
                            };
                            t.useSpherical && (r.useSpherical = !0);
                            const o = n(r);
                            u(I(e, o));
                        } catch (r) {
                            const o = r instanceof Error ? r.message : String(r);
                            u(T(e, "HANDLER_ERROR", `Dipole error: ${o}`));
                        }
                        break;
                    }
                case "cancel":
                    {
                        const { targetRequestId: n } = t;
                        R.set(n, !0);
                        break;
                    }
                default:
                    z0(t);
            }
        } catch (n) {
            const r = n instanceof Error ? n.message : "Unknown handler error";
            u(T(e, "HANDLER_ERROR", r));
        }
    }
    const vr = typeof self < "u";
    vr && (self.onmessage = (t)=>{
        if (!Qe) {
            Pe.push(t.data);
            return;
        }
        qe(t.data);
    }, self.onerror = (t)=>{
        console.error("[Worker] Unhandled error:", typeof t == "string" ? t : "Unknown worker error");
    }, self.onunhandledrejection = (t)=>{
        console.error("[Worker] Unhandled promise rejection:", t.reason);
    }, Mr());
})();
