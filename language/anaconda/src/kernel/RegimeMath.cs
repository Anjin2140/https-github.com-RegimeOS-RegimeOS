// RegimeMath.cs
// Project ANACONDA Core Mathematical Kernel v1.0
// Classification: BLACK PROJECT // SOVEREIGN

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Runtime.CompilerServices;

namespace Anaconda.Kernel
{
    public struct Ternary
    {
        public readonly int Value;

        public Ternary(int value)
        {
            if (value < -1) Value = -1;
            else if (value > 1) Value = 1;
            else Value = value;
        }

        public static readonly Ternary False = new Ternary(-1);
        public static readonly Ternary Unknown = new Ternary(0);
        public static readonly Ternary True = new Ternary(1);

        public static Ternary operator &(Ternary a, Ternary b)
        {
            // Paradox Handler: captures 1 AND -1 -> 0
            if ((a.Value == 1 && b.Value == -1) || (a.Value == -1 && b.Value == 1))
            {
                return Unknown;
            }
            return new Ternary(Math.Min(a.Value, b.Value));
        }

        public static Ternary operator |(Ternary a, Ternary b)
        {
            return new Ternary(Math.Max(a.Value, b.Value));
        }

        public static Ternary operator !(Ternary a)
        {
            return new Ternary(-a.Value);
        }

        public static Ternary operator ^(Ternary a, Ternary b)
        {
            if (a.Value == 0 || b.Value == 0) return Unknown;
            return a.Value == b.Value ? False : True;
        }

        public override bool Equals(object? obj) => obj is Ternary other && Value == other.Value;
        public override int GetHashCode() => Value.GetHashCode();
        public override string ToString() => Value == 1 ? "TRUE" : Value == -1 ? "FALSE" : "UNKNOWN";

        public static implicit operator Ternary(int val) => new Ternary(val);
        public static implicit operator int(Ternary t) => t.Value;
    }

    public class EpsilonStallDetector
    {
        private static readonly System.Threading.ThreadLocal<Dictionary<string, int>> IterationCounts =
            new System.Threading.ThreadLocal<Dictionary<string, int>>(() => new Dictionary<string, int>());

        private static readonly System.Threading.ThreadLocal<Dictionary<string, object>> LastValues =
            new System.Threading.ThreadLocal<Dictionary<string, object>>(() => new Dictionary<string, object>());

        public static Ternary CheckStall(object currentValue, string key, int threshold = 1000)
        {
            var dict = IterationCounts.Value!;
            var valDict = LastValues.Value!;

            if (!dict.ContainsKey(key))
            {
                dict[key] = 1;
                valDict[key] = currentValue;
                return Ternary.Unknown;
            }

            var lastVal = valDict[key];
            if (Equals(lastVal, currentValue))
            {
                dict[key]++;
                if (dict[key] > threshold)
                {
                    // Force a resolution based on dominant trend (default to True/1 for 1 + eps > 1 checks)
                    Console.WriteLine($"[!] WARN_EPSILON_STALL: Loop stall detected at {key}. Forcing resolution to TRUE.");
                    return Ternary.True;
                }
            }
            else
            {
                dict[key] = 1;
                valDict[key] = currentValue;
            }

            return Ternary.Unknown;
        }

        public static void Reset(string key)
        {
            if (IterationCounts.Value!.ContainsKey(key))
            {
                IterationCounts.Value.Remove(key);
                LastValues.Value!.Remove(key);
            }
        }
    }

    public struct RegimeDecimal
    {
        public readonly int Sign; // -1, 0, 1
        public readonly int Exponent;
        public readonly ushort[] Chunks; // Base-65536 digits, MSB first

        private const int BaseVal = 65536;

        public RegimeDecimal(int sign, int exponent, ushort[]? chunks)
        {
            Sign = sign == 0 ? 0 : (sign < 0 ? -1 : 1);
            Exponent = Sign == 0 ? 0 : exponent;
            Chunks = (Sign == 0 || chunks == null) ? Array.Empty<ushort>() : chunks;
            
            // Normalize chunks
            if (Sign != 0)
            {
                int leadingZeros = 0;
                while (leadingZeros < Chunks.Length && Chunks[leadingZeros] == 0)
                {
                    leadingZeros++;
                }

                int trailingZeros = 0;
                while (trailingZeros < Chunks.Length - leadingZeros && Chunks[Chunks.Length - 1 - trailingZeros] == 0)
                {
                    trailingZeros++;
                }

                if (leadingZeros > 0 || trailingZeros > 0)
                {
                    int newLen = Chunks.Length - leadingZeros - trailingZeros;
                    if (newLen <= 0)
                    {
                        Sign = 0;
                        Exponent = 0;
                        Chunks = new ushort[0];
                    }
                    else
                    {
                        ushort[] normChunks = new ushort[newLen];
                        Array.Copy(Chunks, leadingZeros, normChunks, 0, newLen);
                        Chunks = normChunks;
                        Exponent -= leadingZeros;
                    }
                }
            }
        }

        public static readonly RegimeDecimal Zero = new RegimeDecimal(0, 0, null);
        public static readonly RegimeDecimal One = new RegimeDecimal(1, 0, new ushort[] { 1 });

        public static RegimeDecimal FromDouble(double value)
        {
            if (value == 0) return Zero;
            int sign = value < 0 ? -1 : 1;
            double absVal = Math.Abs(value);

            // Convert using fractional scaling
            int exp = (int)Math.Floor(Math.Log(absVal) / Math.Log(BaseVal));
            double scale = absVal / Math.Pow(BaseVal, exp);

            List<ushort> chunks = new List<ushort>();
            for (int i = 0; i < 8; i++) // 8 chunks gives ~128 bits of precision
            {
                int digit = (int)Math.Floor(scale);
                chunks.Add((ushort)digit);
                scale = (scale - digit) * BaseVal;
                if (scale == 0) break;
            }

            return new RegimeDecimal(sign, exp, chunks.ToArray());
        }

        public static RegimeDecimal FromString(string s)
        {
            s = s.Trim();
            if (string.IsNullOrEmpty(s) || s == "0") return Zero;

            int sign = 1;
            if (s.StartsWith("-"))
            {
                sign = -1;
                s = s.Substring(1);
            }
            else if (s.StartsWith("+"))
            {
                s = s.Substring(1);
            }

            string[] parts = s.Split('.');
            BigInteger intPart = BigInteger.Parse(parts[0]);
            BigInteger fracPart = 0;
            BigInteger fracDivisor = 1;

            if (parts.Length > 1)
            {
                string fracStr = parts[1];
                fracPart = BigInteger.Parse(fracStr);
                fracDivisor = BigInteger.Pow(10, fracStr.Length);
            }

            // Represent as Rational: Numerator / Denominator
            BigInteger num = intPart * fracDivisor + fracPart;
            BigInteger den = fracDivisor;

            if (num == 0) return Zero;

            // Divide num by den in Base-65536
            int exp = 0;
            // Align num to be larger than den
            while (num < den)
            {
                num *= BaseVal;
                exp--;
            }
            while (num >= den * BaseVal)
            {
                den *= BaseVal;
                exp++;
            }

            List<ushort> chunks = new List<ushort>();
            for (int i = 0; i < 20; i++) // Higher precision for parsing
            {
                BigInteger digit = num / den;
                chunks.Add((ushort)digit);
                num = (num % den) * BaseVal;
                if (num == 0) break;
            }

            return new RegimeDecimal(sign, exp, chunks.ToArray());
        }

        public double ToDouble()
        {
            if (Sign == 0) return 0.0;
            double val = 0;
            for (int i = 0; i < Chunks.Length; i++)
            {
                val += Chunks[i] * Math.Pow(BaseVal, Exponent - i);
            }
            return Sign * val;
        }

        public override string ToString()
        {
            if (Sign == 0) return "0.0";
            // Formatting output as high-precision decimal string
            BigInteger num = 0;
            for (int i = 0; i < Chunks.Length; i++)
            {
                num = num * BaseVal + Chunks[i];
            }

            int scalePower = Exponent - Chunks.Length + 1;
            if (scalePower >= 0)
            {
                BigInteger finalVal = num * BigInteger.Pow(BaseVal, scalePower);
                return (Sign < 0 ? "-" : "") + finalVal.ToString() + ".0";
            }
            else
            {
                BigInteger den = BigInteger.Pow(BaseVal, -scalePower);
                BigInteger intPart = num / den;
                BigInteger rem = num % den;

                string decFrac = "";
                for (int i = 0; i < 25; i++)
                {
                    rem *= 10;
                    BigInteger d = rem / den;
                    decFrac += d.ToString();
                    rem %= den;
                    if (rem == 0) break;
                }

                return (Sign < 0 ? "-" : "") + intPart.ToString() + "." + (decFrac == "" ? "0" : decFrac);
            }
        }

        public static RegimeDecimal operator +(RegimeDecimal a, RegimeDecimal b)
        {
            if (a.Sign == 0) return b;
            if (b.Sign == 0) return a;

            if (a.Sign != b.Sign)
            {
                // Subtraction fallback
                return a - new RegimeDecimal(-b.Sign, b.Exponent, b.Chunks);
            }

            // Align exponents
            int minExp = Math.Min(a.Exponent - a.Chunks.Length, b.Exponent - b.Chunks.Length);
            int aOffset = a.Exponent - (a.Chunks.Length - 1) - minExp;
            int bOffset = b.Exponent - (b.Chunks.Length - 1) - minExp;

            int len = Math.Max(a.Exponent, b.Exponent) - minExp + 2;
            ushort[] resultChunks = new ushort[len];

            int carry = 0;
            for (int i = 0; i < len; i++)
            {
                int aIdx = a.Chunks.Length - 1 - i + aOffset;
                int bIdx = b.Chunks.Length - 1 - i + bOffset;

                int aDigit = (aIdx >= 0 && aIdx < a.Chunks.Length) ? a.Chunks[aIdx] : 0;
                int bDigit = (bIdx >= 0 && bIdx < b.Chunks.Length) ? b.Chunks[bIdx] : 0;

                int sum = aDigit + bDigit + carry;
                resultChunks[len - 1 - i] = (ushort)(sum % BaseVal);
                carry = sum / BaseVal;
            }

            int finalExp = Math.Max(a.Exponent, b.Exponent) + 1;
            return new RegimeDecimal(a.Sign, finalExp, resultChunks);
        }

        public static RegimeDecimal operator -(RegimeDecimal a, RegimeDecimal b)
        {
            if (b.Sign == 0) return a;
            if (a.Sign == 0) return new RegimeDecimal(-b.Sign, b.Exponent, b.Chunks);

            if (a.Sign != b.Sign)
            {
                return a + new RegimeDecimal(-b.Sign, b.Exponent, b.Chunks);
            }

            // Compare absolute values to determine sign of result
            int cmp = CompareAbsolute(a, b);
            if (cmp == 0) return Zero;

            RegimeDecimal larger = cmp > 0 ? a : b;
            RegimeDecimal smaller = cmp > 0 ? b : a;

            int minExp = Math.Min(larger.Exponent - larger.Chunks.Length, smaller.Exponent - smaller.Chunks.Length);
            int lOffset = larger.Exponent - (larger.Chunks.Length - 1) - minExp;
            int sOffset = smaller.Exponent - (smaller.Chunks.Length - 1) - minExp;

            int len = larger.Exponent - minExp + 1;
            ushort[] resultChunks = new ushort[len];

            int borrow = 0;
            for (int i = 0; i < len; i++)
            {
                int lIdx = larger.Chunks.Length - 1 - i + lOffset;
                int sIdx = smaller.Chunks.Length - 1 - i + sOffset;

                int lDigit = (lIdx >= 0 && lIdx < larger.Chunks.Length) ? larger.Chunks[lIdx] : 0;
                int sDigit = (sIdx >= 0 && sIdx < smaller.Chunks.Length) ? smaller.Chunks[sIdx] : 0;

                int diff = lDigit - sDigit - borrow;
                if (diff < 0)
                {
                    diff += BaseVal;
                    borrow = 1;
                }
                else
                {
                    borrow = 0;
                }
                resultChunks[len - 1 - i] = (ushort)diff;
            }

            int finalSign = cmp > 0 ? a.Sign : -a.Sign;
            return new RegimeDecimal(finalSign, larger.Exponent, resultChunks);
        }

        public static RegimeDecimal operator *(RegimeDecimal a, RegimeDecimal b)
        {
            if (a.Sign == 0 || b.Sign == 0) return Zero;

            int lenA = a.Chunks.Length;
            int lenB = b.Chunks.Length;
            uint[] temp = new uint[lenA + lenB];

            for (int i = 0; i < lenA; i++)
            {
                for (int j = 0; j < lenB; j++)
                {
                    temp[i + j + 1] += (uint)a.Chunks[i] * b.Chunks[j];
                }
            }

            // Carry resolution
            ushort[] resultChunks = new ushort[temp.Length];
            long carry = 0;
            for (int i = temp.Length - 1; i >= 0; i--)
            {
                long val = temp[i] + carry;
                resultChunks[i] = (ushort)(val % BaseVal);
                carry = val / BaseVal;
            }

            int finalExp = a.Exponent + b.Exponent + 1;
            int finalSign = a.Sign * b.Sign;
            return new RegimeDecimal(finalSign, finalExp, resultChunks);
        }

        public static RegimeDecimal operator /(RegimeDecimal a, RegimeDecimal b)
        {
            if (b.Sign == 0) throw new DivideByZeroException();
            if (a.Sign == 0) return Zero;

            // Long division in base 65536
            BigInteger num = 0;
            for (int i = 0; i < a.Chunks.Length; i++)
            {
                num = num * BaseVal + a.Chunks[i];
            }
            BigInteger den = 0;
            for (int i = 0; i < b.Chunks.Length; i++)
            {
                den = den * BaseVal + b.Chunks[i];
            }

            int exp = a.Exponent - b.Exponent;
            while (num < den)
            {
                num *= BaseVal;
                exp--;
            }
            while (num >= den * BaseVal)
            {
                den *= BaseVal;
                exp++;
            }

            List<ushort> chunks = new List<ushort>();
            for (int i = 0; i < 16; i++) // 16 chunks resolution
            {
                BigInteger digit = num / den;
                chunks.Add((ushort)digit);
                num = (num % den) * BaseVal;
                if (num == 0) break;
            }

            return new RegimeDecimal(a.Sign * b.Sign, exp, chunks.ToArray());
        }

        public static bool operator ==(RegimeDecimal a, RegimeDecimal b)
        {
            if (a.Sign != b.Sign) return false;
            if (a.Sign == 0) return true;
            if (a.Exponent != b.Exponent) return false;
            if (a.Chunks.Length != b.Chunks.Length) return false;
            for (int i = 0; i < a.Chunks.Length; i++)
            {
                if (a.Chunks[i] != b.Chunks[i]) return false;
            }
            return true;
        }

        public static bool operator !=(RegimeDecimal a, RegimeDecimal b) => !(a == b);

        public static bool operator >(RegimeDecimal a, RegimeDecimal b)
        {
            if (a.Sign != b.Sign) return a.Sign > b.Sign;
            if (a.Sign == 0) return false;

            int cmp = CompareAbsolute(a, b);
            return a.Sign > 0 ? cmp > 0 : cmp < 0;
        }

        public static bool operator <(RegimeDecimal a, RegimeDecimal b)
        {
            if (a.Sign != b.Sign) return a.Sign < b.Sign;
            if (a.Sign == 0) return false;

            int cmp = CompareAbsolute(a, b);
            return a.Sign > 0 ? cmp < 0 : cmp > 0;
        }

        private static int CompareAbsolute(RegimeDecimal a, RegimeDecimal b)
        {
            if (a.Exponent != b.Exponent) return a.Exponent.CompareTo(b.Exponent);
            int maxLen = Math.Max(a.Chunks.Length, b.Chunks.Length);
            for (int i = 0; i < maxLen; i++)
            {
                int aDigit = i < a.Chunks.Length ? a.Chunks[i] : 0;
                int bDigit = i < b.Chunks.Length ? b.Chunks[i] : 0;
                if (aDigit != bDigit) return aDigit.CompareTo(bDigit);
            }
            return 0;
        }

        public override bool Equals(object? obj) => obj is RegimeDecimal other && this == other;
        public override int GetHashCode()
        {
            int hash = Sign.GetHashCode() ^ Exponent.GetHashCode();
            foreach (var chunk in Chunks) hash ^= chunk.GetHashCode();
            return hash;
        }
    }

    public struct HahnDecimal
    {
        public readonly RegimeDecimal Real;
        public readonly int EpsilonCoeff;

        public HahnDecimal(RegimeDecimal real, int epsCoeff = 0)
        {
            Real = real;
            EpsilonCoeff = epsCoeff;
        }

        public static implicit operator HahnDecimal(RegimeDecimal r) => new HahnDecimal(r, 0);

        public static HahnDecimal operator +(HahnDecimal a, HahnDecimal b)
        {
            return new HahnDecimal(a.Real + b.Real, a.EpsilonCoeff + b.EpsilonCoeff);
        }

        public static HahnDecimal operator -(HahnDecimal a, HahnDecimal b)
        {
            return new HahnDecimal(a.Real - b.Real, a.EpsilonCoeff - b.EpsilonCoeff);
        }

        public static HahnDecimal operator *(HahnDecimal a, HahnDecimal b)
        {
            // Infinitesimal multiplication rules: (a + b*eps) * (c + d*eps) = a*c + (a*d + b*c)*eps
            // eps^2 is discarded.
            var real = a.Real * b.Real;
            var eps = (a.Real.ToDouble() * b.EpsilonCoeff) + (b.Real.ToDouble() * a.EpsilonCoeff);
            return new HahnDecimal(real, (int)Math.Round(eps));
        }

        public static Ternary operator >(HahnDecimal a, HahnDecimal b)
        {
            string callerKey = GetCallerKey();
            Ternary stallCheck = EpsilonStallDetector.CheckStall(a.Real, callerKey);
            if (stallCheck.Value != 0) return stallCheck;

            if (a.Real > b.Real) return Ternary.True;
            if (a.Real < b.Real) return Ternary.False;

            // Real parts are equal, compare epsilon coefficients
            if (a.EpsilonCoeff > b.EpsilonCoeff) return Ternary.True;
            if (a.EpsilonCoeff < b.EpsilonCoeff) return Ternary.False;

            return Ternary.Unknown; // Equal
        }

        public static Ternary operator <(HahnDecimal a, HahnDecimal b)
        {
            string callerKey = GetCallerKey();
            Ternary stallCheck = EpsilonStallDetector.CheckStall(a.Real, callerKey);
            if (stallCheck.Value != 0) return !stallCheck;

            if (a.Real < b.Real) return Ternary.True;
            if (a.Real > b.Real) return Ternary.False;

            if (a.EpsilonCoeff < b.EpsilonCoeff) return Ternary.True;
            if (a.EpsilonCoeff > b.EpsilonCoeff) return Ternary.False;

            return Ternary.Unknown; // Equal
        }

        private static string GetCallerKey()
        {
            var stack = new StackTrace();
            for (int i = 2; i < stack.FrameCount; i++)
            {
                var frame = stack.GetFrame(i);
                if (frame == null) continue;
                var method = frame.GetMethod();
                if (method != null && method.DeclaringType?.FullName != null && !method.DeclaringType.FullName.Contains("HahnDecimal"))
                {
                    return $"{method.DeclaringType.FullName}.{method.Name}:{frame.GetILOffset()}";
                }
            }
            return "unknown_context";
        }

        public override string ToString()
        {
            if (EpsilonCoeff == 0) return Real.ToString();
            return $"{Real} + {EpsilonCoeff}ε";
        }
    }
}
