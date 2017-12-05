FROM starcraft:java

COPY replay-parser/parser-jar-with-dependencies.jar parser.jar

CMD ["win_java32", "-jar", "parser.jar"]
