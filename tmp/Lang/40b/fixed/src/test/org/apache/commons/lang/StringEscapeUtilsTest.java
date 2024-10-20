/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.commons.lang;

import java.io.IOException;
import java.io.StringWriter;
import java.lang.reflect.Constructor;
import java.lang.reflect.Modifier;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;
import junit.textui.TestRunner;

/**
 * Unit tests for {@link StringEscapeUtils}.
 *
 * @author <a href="mailto:alex@purpletech.com">Alexander Day Chaffee</a>
 * @version $Id$
 */
public class StringEscapeUtilsTest extends TestCase {
    private final static String FOO = "foo";

    public StringEscapeUtilsTest(String name) {
        super(name);
    }

    public static void main(String[] args) {
        TestRunner.run(suite());
    }

    public static Test suite() {
        TestSuite suite = new TestSuite(StringEscapeUtilsTest.class);
        suite.setName("StringEscapeUtilsTest Tests");
        return suite;
    }

    //-----------------------------------------------------------------------
    public void testConstructor() {
        assertNotNull(new StringEscapeUtils());
        Constructor[] cons = StringEscapeUtils.class.getDeclaredConstructors();
        assertEquals(1, cons.length);
        assertEquals(true, Modifier.isPublic(cons[0].getModifiers()));
        assertEquals(true, Modifier.isPublic(StringEscapeUtils.class.getModifiers()));
        assertEquals(false, Modifier.isFinal(StringEscapeUtils.class.getModifiers()));
    }
    
    //-----------------------------------------------------------------------
    public void testEscapeJava() throws IOException {
        assertEquals(null, StringEscapeUtils.escapeJava(null));
        try {
            StringEscapeUtils.escapeJava(null, null);
            fail();
        } catch (IOException ex) {
            fail();
        } catch (IllegalArgumentException ex) {
        }
        try {
            StringEscapeUtils.escapeJava(null, "");
            fail();
        } catch (IOException ex) {
            fail();
        } catch (IllegalArgumentException ex) {
        }
        
        assertEscapeJava("empty string", "", "");
        assertEscapeJava(FOO, FOO);
        assertEscapeJava("tab", "\\t", "\t");
        assertEscapeJava("backslash", "\\\\", "\\");
        assertEscapeJava("single quote should not be escaped", "'", "'");
        assertEscapeJava("\\\\\\b\\t\\r", "\\\b\t\r");
        assertEscapeJava("\\u1234", "\u1234");
        assertEscapeJava("\\u0234", "\u0234");
        assertEscapeJava("\\u00EF", "\u00ef");
        assertEscapeJava("\\u0001", "\u0001");
        assertEscapeJava("Should use capitalized unicode hex", "\\uABCD", "\uabcd");

        assertEscapeJava("He didn't say, \\\"stop!\\\"",
                "He didn't say, \"stop!\"");
        assertEscapeJava("non-breaking space", "This space is non-breaking:" + "\\u00A0",
                "This space is non-breaking:\u00a0");
        assertEscapeJava("\\uABCD\\u1234\\u012C",
                "\uABCD\u1234\u012C");
    }

    /**
     * https://issues.apache.org/jira/browse/LANG-421
     */
    public void testEscapeJavaWithSlash() {
        final String input = "String with a slash (/) in it";

        final String expected = input;
        final String actual = StringEscapeUtils.escapeJava(input);

        /**
         * In 2.4 StringEscapeUtils.escapeJava(String) escapes '/' characters, which are not a valid character to escape
         * in a Java string.
         */
        assertEquals(expected, actual);
    }
    
    private void assertEscapeJava(String escaped, String original) throws IOException {
        assertEscapeJava(null, escaped, original);
    }

    private void assertEscapeJava(String message, String expected, String original) throws IOException {
        String converted = StringEscapeUtils.escapeJava(original);
        message = "escapeJava(String) failed" + (message == null ? "" : (": " + message));
        assertEquals(message, expected, converted);

        StringWriter writer = new StringWriter();
        StringEscapeUtils.escapeJava(writer, original);
        assertEquals(expected, writer.toString());
    }

    public void testUnescapeJava() throws IOException {
        assertEquals(null, StringEscapeUtils.unescapeJava(null));
        try {
            StringEscapeUtils.unescapeJava(null, null);
            fail();
        } catch (IOException ex) {
            fail();
        } catch (IllegalArgumentException ex) {
        }
        try {
            StringEscapeUtils.unescapeJava(null, "");
            fail();
        } catch (IOException ex) {
            fail();
        } catch (IllegalArgumentException ex) {
        }
        try {
            StringEscapeUtils.unescapeJava("\\u02-3");
            fail();
        } catch (RuntimeException ex) {
        }
        
        assertUnescapeJava("", "");
        assertUnescapeJava("test", "test");
        assertUnescapeJava("\ntest\b", "\\ntest\\b");
        assertUnescapeJava("\u123425foo\ntest\b", "\\u123425foo\\ntest\\b");
        assertUnescapeJava("'\foo\teste\r", "\\'\\foo\\teste\\r");
        assertUnescapeJava("", "\\");
        //foo
        assertUnescapeJava("lowercase unicode", "\uABCDx", "\\uabcdx");
        assertUnescapeJava("uppercase unicode", "\uABCDx", "\\uABCDx");
        assertUnescapeJava("unicode as final character", "\uABCD", "\\uabcd");
    }

    private void assertUnescapeJava(String unescaped, String original) throws IOException {
        assertUnescapeJava(null, unescaped, original);
    }

    private void assertUnescapeJava(String message, String unescaped, String original) throws IOException {
        String expected = unescaped;
        String actual = StringEscapeUtils.unescapeJava(original);

        assertEquals("unescape(String) failed" +
                (message == null ? "" : (": " + message)) +
                ": expected '" + StringEscapeUtils.escapeJava(expected) +
                // we escape this so we can see it in the error message
                "' actual '" + StringEscapeUtils.escapeJava(actual) + "'",
                expected, actual);

        StringWriter writer = new StringWriter();
        StringEscapeUtils.unescapeJava(writer, original);
        assertEquals(unescaped, writer.toString());

    }

    public void testEscapeJavaScript() {
        assertEquals(null, StringEscapeUtils.escapeJavaScript(null));
        try {
            StringEscapeUtils.escapeJavaScript(null, null);
            fail();
        } catch (IOException ex) {
            fail();
        } catch (IllegalArgumentException ex) {
        }
        try {
            StringEscapeUtils.escapeJavaScript(null, "");
            fail();
        } catch (IOException ex) {
            fail();
        } catch (IllegalArgumentException ex) {
        }
        
        assertEquals("He didn\\'t say, \\\"stop!\\\"", StringEscapeUtils.escapeJavaScript("He didn't say, \"stop!\""));
        assertEquals("document.getElementById(\\\"test\\\").value = \\'<script>alert(\\'aaa\\');<\\/script>\\';", 
                StringEscapeUtils.escapeJavaScript("document.getElementById(\"test\").value = '<script>alert('aaa');</script>';"));
    }


    // HTML and XML
    //--------------------------------------------------------------

    String[][] htmlEscapes = {
        {"no escaping", "plain text", "plain text"},
        {"no escaping", "plain text", "plain text"},
        {"empty string", "", ""},
        {"null", null, null},
        {"ampersand", "bread &amp; butter", "bread & butter"},
        {"quotes", "&quot;bread&quot; &amp; butter", "\"bread\" & butter"},
        {"final character only", "greater than &gt;", "greater than >"},
        {"first character only", "&lt; less than", "< less than"},
        {"apostrophe", "Huntington's chorea", "Huntington's chorea"},
        {"languages", "English,Fran&ccedil;ais,&#26085;&#26412;&#35486; (nihongo)", "English,Fran\u00E7ais,\u65E5\u672C\u8A9E (nihongo)"},
        {"8-bit ascii doesn't number-escape", "~\u007F", "\u007E\u007F"},
        {"8-bit ascii does number-escape", "&#128;&#159;", "\u0080\u009F"},
    };

    public void testEscapeHtml() {
        for (int i = 0; i < htmlEscapes.length; ++i) {
            String message = htmlEscapes[i][0];
            String expected = htmlEscapes[i][1];
            String original = htmlEscapes[i][2];
            assertEquals(message, expected, StringEscapeUtils.escapeHtml(original));
            StringWriter sw = new StringWriter();
            try {
                StringEscapeUtils.escapeHtml(sw, original);
            } catch (IOException e) {
            }
            String actual = original == null ? null : sw.toString();
            assertEquals(message, expected, actual);
        }
    }

    public void testUnescapeHtml() {
        for (int i = 0; i < htmlEscapes.length; ++i) {
            String message = htmlEscapes[i][0];
            String expected = htmlEscapes[i][2];
            String original = htmlEscapes[i][1];
            assertEquals(message, expected, StringEscapeUtils.unescapeHtml(original));
            
            StringWriter sw = new StringWriter();
            try {
                StringEscapeUtils.unescapeHtml(sw, original);
            } catch (IOException e) {
            }
            String actual = original == null ? null : sw.toString();
            assertEquals(message, expected, actual);
        }
        // \u00E7 is a cedilla (c with wiggle under)
        // note that the test string must be 7-bit-clean (unicode escaped) or else it will compile incorrectly
        // on some locales        
        assertEquals("funny chars pass through OK", "Fran\u00E7ais", StringEscapeUtils.unescapeHtml("Fran\u00E7ais"));
        
        assertEquals("Hello&;World", StringEscapeUtils.unescapeHtml("Hello&;World"));
        assertEquals("Hello&#;World", StringEscapeUtils.unescapeHtml("Hello&#;World"));
        assertEquals("Hello&# ;World", StringEscapeUtils.unescapeHtml("Hello&# ;World"));
        assertEquals("Hello&##;World", StringEscapeUtils.unescapeHtml("Hello&##;World"));
    }

    public void testUnescapeHexCharsHtml() {
        // Simple easy to grok test 
        assertEquals("hex number unescape", "\u0080\u009F", StringEscapeUtils.unescapeHtml("&#x80;&#x9F;"));
        assertEquals("hex number unescape", "\u0080\u009F", StringEscapeUtils.unescapeHtml("&#X80;&#X9F;"));
        // Test all Character values:
        for (char i = Character.MIN_VALUE; i < Character.MAX_VALUE; i++) {
            Character c1 = new Character(i);
            Character c2 = new Character((char)(i+1));
            String expected = c1.toString() + c2.toString();
            String escapedC1 = "&#x" + Integer.toHexString((c1.charValue())) + ";";
            String escapedC2 = "&#x" + Integer.toHexString((c2.charValue())) + ";";
            assertEquals("hex number unescape index " + (int)i, expected, StringEscapeUtils.unescapeHtml(escapedC1 + escapedC2));
        }
    }

    public void testUnescapeUnknownEntity() throws Exception
    {
        assertEquals("&zzzz;", StringEscapeUtils.unescapeHtml("&zzzz;"));
    }

    public void testEscapeHtmlVersions() throws Exception
    {
        assertEquals("&Beta;", StringEscapeUtils.escapeHtml("\u0392"));
        assertEquals("\u0392", StringEscapeUtils.unescapeHtml("&Beta;"));

        //todo: refine API for escaping/unescaping specific HTML versions

    }

    public void testEscapeXml() throws Exception {
        assertEquals("&lt;abc&gt;", StringEscapeUtils.escapeXml("<abc>"));
        assertEquals("<abc>", StringEscapeUtils.unescapeXml("&lt;abc&gt;"));

        assertEquals("XML should use numbers, not names for HTML entities",
                "&#161;", StringEscapeUtils.escapeXml("\u00A1"));
        assertEquals("XML should use numbers, not names for HTML entities",
                "\u00A0", StringEscapeUtils.unescapeXml("&#160;"));

        assertEquals("ain't", StringEscapeUtils.unescapeXml("ain&apos;t"));
        assertEquals("ain&apos;t", StringEscapeUtils.escapeXml("ain't"));
        assertEquals("", StringEscapeUtils.escapeXml(""));
        assertEquals(null, StringEscapeUtils.escapeXml(null));
        assertEquals(null, StringEscapeUtils.unescapeXml(null));

        StringWriter sw = new StringWriter();
        try {
            StringEscapeUtils.escapeXml(sw, "<abc>");
        } catch (IOException e) {
        }
        assertEquals("XML was escaped incorrectly", "&lt;abc&gt;", sw.toString() );

        sw = new StringWriter();
        try {
            StringEscapeUtils.unescapeXml(sw, "&lt;abc&gt;");
        } catch (IOException e) {
        }
        assertEquals("XML was unescaped incorrectly", "<abc>", sw.toString() );
    }

    // Tests issue #38569
    // http://issues.apache.org/bugzilla/show_bug.cgi?id=38569
    public void testStandaloneAmphersand() {
        assertEquals("<P&O>", StringEscapeUtils.unescapeHtml("&lt;P&O&gt;"));
        assertEquals("test & <", StringEscapeUtils.unescapeHtml("test & &lt;"));
        assertEquals("<P&O>", StringEscapeUtils.unescapeXml("&lt;P&O&gt;"));
        assertEquals("test & <", StringEscapeUtils.unescapeXml("test & &lt;"));
    }

    public void testLang313() {
        assertEquals("& &", StringEscapeUtils.unescapeHtml("& &amp;"));
    }

    public void testEscapeCsvString() throws Exception
    {
        assertEquals("foo.bar",          StringEscapeUtils.escapeCsv("foo.bar"));
        assertEquals("\"foo,bar\"",      StringEscapeUtils.escapeCsv("foo,bar"));
        assertEquals("\"foo\nbar\"",     StringEscapeUtils.escapeCsv("foo\nbar"));
        assertEquals("\"foo\rbar\"",     StringEscapeUtils.escapeCsv("foo\rbar"));
        assertEquals("\"foo\"\"bar\"",   StringEscapeUtils.escapeCsv("foo\"bar"));
        assertEquals("",   StringEscapeUtils.escapeCsv(""));
        assertEquals(null, StringEscapeUtils.escapeCsv(null));
    }

    public void testEscapeCsvWriter() throws Exception
    {
        checkCsvEscapeWriter("foo.bar",        "foo.bar");
        checkCsvEscapeWriter("\"foo,bar\"",    "foo,bar");
        checkCsvEscapeWriter("\"foo\nbar\"",   "foo\nbar");
        checkCsvEscapeWriter("\"foo\rbar\"",   "foo\rbar");
        checkCsvEscapeWriter("\"foo\"\"bar\"", "foo\"bar");
        checkCsvEscapeWriter("", null);
        checkCsvEscapeWriter("", "");
    }

    private void checkCsvEscapeWriter(String expected, String value) {
        try {
            StringWriter writer = new StringWriter();
            StringEscapeUtils.escapeCsv(writer, value);
            assertEquals(expected, writer.toString());
        } catch (IOException e) {
            fail("Threw: " + e);
        }
    }

    public void testUnescapeCsvString() throws Exception
    {
        assertEquals("foo.bar",          StringEscapeUtils.unescapeCsv("foo.bar"));
        assertEquals("foo,bar",      StringEscapeUtils.unescapeCsv("\"foo,bar\""));
        assertEquals("foo\nbar",     StringEscapeUtils.unescapeCsv("\"foo\nbar\""));
        assertEquals("foo\rbar",     StringEscapeUtils.unescapeCsv("\"foo\rbar\""));
        assertEquals("foo\"bar",   StringEscapeUtils.unescapeCsv("\"foo\"\"bar\""));
        assertEquals("",   StringEscapeUtils.unescapeCsv(""));
        assertEquals(null, StringEscapeUtils.unescapeCsv(null));

        assertEquals("\"foo.bar\"",          StringEscapeUtils.unescapeCsv("\"foo.bar\""));
    }

    public void testUnescapeCsvWriter() throws Exception
    {
        checkCsvUnescapeWriter("foo.bar",        "foo.bar");
        checkCsvUnescapeWriter("foo,bar",    "\"foo,bar\"");
        checkCsvUnescapeWriter("foo\nbar",   "\"foo\nbar\"");
        checkCsvUnescapeWriter("foo\rbar",   "\"foo\rbar\"");
        checkCsvUnescapeWriter("foo\"bar", "\"foo\"\"bar\"");
        checkCsvUnescapeWriter("", null);
        checkCsvUnescapeWriter("", "");

        checkCsvUnescapeWriter("\"foo.bar\"",        "\"foo.bar\"");
    }

    private void checkCsvUnescapeWriter(String expected, String value) {
        try {
            StringWriter writer = new StringWriter();
            StringEscapeUtils.unescapeCsv(writer, value);
            assertEquals(expected, writer.toString());
        } catch (IOException e) {
            fail("Threw: " + e);
        }
    }

    // https://issues.apache.org/jira/browse/LANG-480
    public void testEscapeHtmlHighUnicode() throws java.io.UnsupportedEncodingException {
        // this is the utf8 representation of the character:
        // COUNTING ROD UNIT DIGIT THREE
        // in unicode
        // codepoint: U+1D362
        byte[] data = new byte[] { (byte)0xF0, (byte)0x9D, (byte)0x8D, (byte)0xA2 };

        String escaped = StringEscapeUtils.escapeHtml( new String(data, "UTF8") );
        String unescaped = StringEscapeUtils.unescapeHtml( escaped );

        assertEquals( "High unicode was not escaped correctly", "&#119650;", escaped);
    }

    // https://issues.apache.org/jira/browse/LANG-339
    public void testEscapeHiragana() throws java.io.UnsupportedEncodingException {
        // Some random Japanese unicode characters
        String escaped = StringEscapeUtils.escapeHtml( "\u304B\u304C\u3068" );
        assertEquals( "Hiragana character unicode behaviour has changed from their being escaped", 
        "&#12363;&#12364;&#12392;", escaped);

        String unescaped = StringEscapeUtils.unescapeHtml( escaped );

        assertEquals( "Hiragana character unicode behaviour has changed - expected no unescaping", escaped, escaped);
    }
}
