# 3AC-interpreteer

To run use file interpret.py

Example input:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<program language="IPPcode18">


    <instruction order="1" opcode="JUMP">
        <arg1 type="label">start_of_program</arg1>
    </instruction>

    <instruction order="2" opcode="LABEL">
        <arg1 type="label">double_x</arg1>
    </instruction>

    <instruction order="3" opcode="CREATEFRAME"/>
    <instruction order="4" opcode="PUSHFRAME"/>




    <instruction order="5" opcode="DEFVAR">
        <arg1 type="var">LF@y</arg1>
    </instruction>

    <instruction order="6" opcode="ADD">
        <arg1 type="var">LF@y</arg1>
        <arg2 type="int">15</arg2>
        <arg3 type="int">15</arg3>
    </instruction>

    <instruction order="7" opcode="WRITE">
        <arg1 type="var">LF@y</arg1>
    </instruction>


    <instruction order="8" opcode="MOVE">
        <arg1 type="var">GF@x</arg1>
        <arg2 type="var">LF@y</arg2>
    </instruction>

    <instruction order="9" opcode="POPFRAME"/>

    <instruction order="10" opcode="RETurn"/>


    <instruction order="11" opcode="LABEL">
        <arg1 type="label">lol_function</arg1>
    </instruction>

    <instruction order="12" opcode="CREATEFRAME"/>
    <instruction order="13" opcode="PUSHFRAME"/>

    <instruction order="14" opcode="DEFVAR">
        <arg1 type="var">LF@x</arg1>
    </instruction>


    <instruction order="15" opcode="DEFVAR">
        <arg1 type="var">LF@y</arg1>
    </instruction>

    <instruction order="16" opcode="ADD">
        <arg1 type="var">LF@x</arg1>
        <arg2 type="var">GF@x</arg2>
        <arg3 type="var">GF@y</arg3>
    </instruction>

    <instruction order="17" opcode="MUL">
        <arg1 type="var">LF@y</arg1>
        <arg2 type="var">GF@x</arg2>
        <arg3 type="var">GF@y</arg3>
    </instruction>


    <instruction order="18" opcode="WRITE">
        <arg1 type="string">Y BEFORE CALL:</arg1>
    </instruction>

    <instruction order="19" opcode="WRITE">
        <arg1 type="var">LF@y</arg1>
    </instruction>


    <instruction order="20" opcode="CALL">
        <arg1 type="label">double_x</arg1>
    </instruction>

    <instruction order="21" opcode="CALL">
        <arg1 type="label">double_x</arg1>
    </instruction>


    <instruction order="22" opcode="WRITE">
        <arg1 type="string">Y AFTER CALL:</arg1>
    </instruction>

    <instruction order="23" opcode="WRITE">
        <arg1 type="var">LF@y</arg1>
    </instruction>


    <instruction order="24" opcode="WRITE">
        <arg1 type="var">LF@x</arg1>
    </instruction>


    <instruction order="25" opcode="IDIV">
        <arg1 type="var">GF@result</arg1>
        <arg2 type="var">LF@y</arg2>
        <arg3 type="var">LF@x</arg3>
    </instruction>

    <instruction order="26" opcode="POPFRAME"/>

    <instruction order="27" opcode="RETURN"/>



    <instruction order="28" opcode="LABEL">
        <arg1 type="label">start_of_program</arg1>
    </instruction>


    <instruction order="29" opcode="DEFVAR">
        <arg1 type="var">GF@x</arg1>
    </instruction>

    <instruction order="30" opcode="DEFVAR">
        <arg1 type="var">GF@y</arg1>
    </instruction>

    <instruction order="31" opcode="DEFVAR">
        <arg1 type="var">GF@result</arg1>
    </instruction>

    <instruction order="32" opcode="MOVE">
        <arg1 type="var">GF@x</arg1>
        <arg2 type="int">10</arg2>
    </instruction>

    <instruction order="33" opcode="MOVE">
        <arg1 type="var">GF@y</arg1>
        <arg2 type="int">5</arg2>
    </instruction>

    <instruction order="34" opcode="CALL">
        <arg1 type="label">lol_function</arg1>
    </instruction>

    <instruction order="35" opcode="WRITE">
        <arg1 type="string">END_OF_PROGRAM</arg1>
    </instruction>

    <!--<instruction order="36" opcode="WRITE">-->
        <!--<arg1 type="var">LF@y</arg1>-->
    <!--</instruction>-->

    <instruction order="36" opcode="WRITE">
        <arg1 type="var">GF@result</arg1>
    </instruction>

</program>
```

