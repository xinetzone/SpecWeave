[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

An alternative to Postman that supports editing GraphQL queries directly and autoload your GraphQL schema.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A GraphQL API to query and mutate data across APIs like Salesforce, HubSpot, Microsoft Dynamics, Pipedrive, and many more.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Apache APISIX is a dynamic, real-time, high-performance API gateway providing rich traffic management features such as load balancing, dynamic upstream, canary release, observability, etc. As a cloud-native API gateway, Apache APISIX already can support GraphQL syntax at the beginning of its design. Efficiently matching GraphQL statements carried in requests can filter out abnormal traffic to further ensure security. For more information, please visit [How to Use GraphQL with API Gateway Apache APISIX](https://apisix.apache.org/blog/2022/03/02/apisix-integration-graphql-plugin/)[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A Model Context Protocol server that exposes GraphQL operations as tools for AI models to access and orchestrate APIs running with Apollo.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A cloud service that helps you build, validate, monitor and secure your organizations data graph.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Fully managed GraphQL service with realtime subscriptions, offline programming & synchronization, and enterprise security features as well as fine grained authorization controls.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Fully managed GraphQL backend based on open source Parse Platform. Store and query relational data, run cloud functions and more over GraphQL API. Free to get started.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

[Beeceptor](https://beeceptor.com/graphql-mock-server/?utm_source=graphql_org) is a no-code, cloud-based platform that enables creating **GraphQL Mock Servers** directly from your SDL schema with type-safe APIs containing **AI-enhanced realistic data**. It doubles as an HTTP Debugging Proxy to inspect and selectively mock all API traffic (GraphQL, REST, SOAP).[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Dgraph is a native GraphQL database with a graph backend. This means Dgraph is not an interface on top of an existing database like Postgres but is actually designed from the ground-up for GraphQL. It is optimized for speed and performance, depending on multiple computer science breakthroughs to get the best result. Dgraph Cloud is a fully managed GraphQL backend service that lets you iterate faster, without worrying about your infrastructure.

README

Install Steps if running locally on linux not on Dgraph Cloud:

```
docker pull dgraph/standalone
mkdir -p ~/dgraph
docker run -it -p 5080:5080 -p 6080:6080 -p 8080:8080 \
  -p 9080:9080 -p 8000:8000 -v ~/dgraph:/dgraph --name dgraph \
  dgraph/standalone:master
```

Set your GraphQL Schema:

```
touch schema.graphql
nano schema.graphql
```

```
type Product {
  id: ID!
  name: String! @id
  reviews: [Review] @hasInverse(field: about)
}
 
type Customer {
  username: String! @id
  reviews: [Review] @hasInverse(field: by)
}
 
type Review {
  id: ID!
  about: Product!
  by: Customer!
  comment: String @search(by: [fulltext])
  rating: Int @search
}
```

```
curl -X POST localhost:8080/admin/schema --data-binary '@schema.graphql'
```

Fire up your favorite GraphQL Client pointed at `http://localhost:8080/graphql` and run mutations and queries

```
mutation {
  addProduct(input: [{ name: "Dgraph" }, { name: "Dgraph Cloud" }]) {
    product {
      id
      name
    }
  }
  addCustomer(input: [{ username: "TonyStark" }]) {
    customer {
      username
    }
  }
}
```

```
mutation {
  addReview(
    input: [
      {
        by: { username: "TonyStark" }
        about: { name: "Dgraph" }
        comment: "Fantastic, easy to install, worked great. Best GraphQL server available"
        rating: 10
      }
    ]
  ) {
    review {
      id
      comment
      rating
      by {
        username
      }
      about {
        id
        name
      }
    }
  }
}
```

```
query {
  queryReview(
    filter: { comment: { alloftext: "server easy install" }, rating: { gt: 5 } }
  ) {
    comment
    by {
      username
      reviews(order: { desc: rating }, first: 10) {
        about {
          name
          reviews(order: { asc: rating }, first: 5) {
            by {
              username
            }
            comment
            rating
          }
        }
        rating
      }
    }
    about {
      name
    }
  }
}
```[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A Java library that can expose a JPA annotated data model as a GraphQL service over any relational database.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Live GraphQL Security & Compliance. Ensure your GraphQL endpoints are production-ready. During development. Without needed configuration. Supports every language and framework. Free to get started.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Create an instant GraphQL backend by importing a gql schema. The database will create relations and indexes for you, so you'll be ready to query in seconds, without writing any database code. Serverless pricing, free to get started.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Headless CMS that pairs a modern content editing experience with robust content personalisation and scheduling capabilities. It delivers your content through a blazing-fast, API-first delivery using GraphQL and REST endpoints.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Grafbase provides secure self-hosted deployment options for GraphQL Federation, unmatched query speed, advanced governance, and unified data access for reliable, enterprise-grade API management. Learn more about scaling GraphQL Federation with [Grafbase](https://grafbase.com/).[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

graphapi® is a secure low-code GraphQL-as-a-service platform. Based on the input data model, it auto-generates the GraphQL schema, all resolvers, and the database stack. Additionally, it provides a user interface allowing teams to manage their data. For more information, go to [graphapi.com](https://graphapi.com/).[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Fast and free security scan to run a dozen of tests on a GraphQL endpoint. No login is required.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Hasura connects to your databases & microservices and instantly gives you a production-ready GraphQL API.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Hive is a fully open-source schema registry, analytics and gateway for GraphQL federation and other GraphQL APIs.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Hygraph is the federated content platform that allows true composability of your stack. Integrate all your services with a unique content federation approach and distribute content from anywhere - to anywhere using a single, powerful GraphQL API.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Insomnia is an open-source, cross-platform API Client for GraphQL, REST, and gRPC. Insomnia combines an easy-to-use interface with advanced functionality like authentication helpers, code generation, and environment variables.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A headless CMS (Content Management System) that combines powerful content personalisation and scheduling capabilities with a modern content editing experience and a blazing fast GraphQL/REST content delivery API.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A Model Context Protocol server enabling LLMs to interact with GraphQL APIs through schema introspection and query execution capabilities.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A GraphQL analaytics and monitoring Service to find functional and performance issues.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A GraphQL API management platform by [ChilliCream](https://chillicream.com/?utm_source=graphql_org&utm_medium=referral) that lets you explore, test, and monitor your APIs. It includes schema and client registries, telemetry, federation support, and a full-featured GraphQL IDE.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

A robust multi-protocol API client with features like API scripting, automation, collaborative workspaces, and comprehensive support for testing and developing GraphQL APIs.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Tyk is a lightweight Open Source API Management Gateway that has built a Full API Life-Cycle Management around GraphQL with its own GraphQL engine that is written in Golang. Tyk supports schema stitching of multiple GraphQL and/or REST APIs through [Universal Data Graph (UDG)](https://tyk.io/docs/universal-data-graph/) as well as [GraphQL Federation](https://tyk.io/docs/getting-started/key-concepts/graphql-federation/) and [GraphQL Subscription](https://tyk.io/docs/getting-started/key-concepts/graphql-subscriptions/).[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Typetta is an open-source ORM written in TypeScript that aims to allow seamless access to data in a typed fashion to all main SQL databases (MySQL, PostgreSQL, Microsoft SQL Server, SQLLite3, CockroachDB, MariaDB, Oracle & Amazon Redshift) and also to the NoSQL database MongoDB.[Services](https://graphql.org/community/tools-and-libraries/?tags=services)

Webiny allows you to quickly build GraphQL APIs on top of AWS Lambda and DynamoDB with built-in scaffolds. Webiny also includes a ready-made headless GraphQL CMS for a no-code experience.[Ballerina](https://graphql.org/community/tools-and-libraries/?tags=ballerina)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

The Ballerina Standard Library Package for consume GraphQL services.

README

To run a `ballerina-graphql` client:

- Download and install [Ballerina Language](https://ballerina.io/downloads)
- Then run `bal run graphql_client.bal` to run the service, with this code in the `graphql_client.bal` file:

```
import ballerina/graphql;
import ballerina/io;
 
type Response record {
    record { string hello; } data;
};
 
public function main() returns error? {
    graphql:Client helloClient = check new ("localhost:9090/graphql");
    string document = "{ hello }";
    Response response = check helloClient->execute(document);
    io:println(response.data.hello);
}
```

**Features**
- Dependently-typed response retrieval with Ballerina type inferring
- Custom client generation support[Ballerina](https://graphql.org/community/tools-and-libraries/?tags=ballerina)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

The Ballerina Standard Library Package for write GraphQL services.

README

To run a `ballerina-graphql` hello world server:

- Download and install [Ballerina Language](https://ballerina.io/downloads)
- Then run `bal run graphql_service.bal` to run the service, with this code in the `graphql_service.bal` file:

```
import ballerina/graphql;
 
service /graphql on new graphql:Listener(9090) {
    resource function get hello() returns string {
        return "Hello, world!";
    }
}
```

**Features**
- Built with Ballerina `service` and `listener` model, which are first-class citizens in Ballerina
- Supports subscriptions over websocket (No additional libraries needed)
- Supports file upload
- Built-in GraphiQL client

A C++20 GraphQL request client generator and response parser using the schema document. If you want to consume a GraphQL service from a C++ client, you can pre-compile queries and deserialization functions for the expected results.

README

The `clientgen` utility is based on `schemagen` and shares the same external dependencies. The command line arguments are almost the same, except it takes an extra file for the request document and there is no equivalent to `--stubs`:

```
Usage:  clientgen [options] <schema file> <request file> <output filename prefix> <output namespace>
Command line options:
  --version              Print the version number
  -? [ --help ]          Print the command line options
  -v [ --verbose ]       Verbose output including generated header names as
                         well as sources
  -s [ --schema ] arg    Schema definition file path
  -r [ --request ] arg   Request document file path
  -o [ --operation ] arg Operation name if the request document contains more
                         than one
  -p [ --prefix ] arg    Prefix to use for the generated C++ filenames
  -n [ --namespace ] arg C++ sub-namespace for the generated types
  --source-dir arg       Target path for the <prefix>Client.cpp source file
  --header-dir arg       Target path for the <prefix>Client.h header file
  --no-introspection     Do not expect support for Introspection
```

This utility should output one header and one source file for each request document. A request document may contain more than one operation, in which case it will output definitions for all of them together. You may limit the output to a single operation from the request document by specifying the `--operation` (or `-o`) argument with the operation name.

The generated code depends on the `graphqlclient` library for serialization of built-in types. If you link the generated code, you’ll also need to link `graphqlclient`, `graphqlpeg` for the pre-parsed, pre-validated request AST, and `graphqlresponse` for the `graphql::response::Value` implementation.

A C++20 GraphQL service generator using the schema document. You can use this to implement a GraphQL service with resolvers backed by whatever C++ libraries you need.

README

Run `schemagen -?` to get a list of options. Many of the files in the [samples](https://github.com/microsoft/cppgraphqlgen/tree/main/samples) directory were generated with `schemagen`, you can look at [samples/learn/schema/CMakeLists.txt](https://github.com/microsoft/cppgraphqlgen/blob/main/samples/learn/schema/CMakeLists.txt) for an example of how to call it with the canonical Star Wars sample [schema](https://github.com/microsoft/cppgraphqlgen/blob/main/samples/learn/schema/schema.learn.graphql):

```
Usage:  schemagen [options] <schema file> <output filename prefix> <output namespace>
Command line options:
  --version              Print the version number
  -? [ --help ]          Print the command line options
  -v [ --verbose ]       Verbose output including generated header names as
                         well as sources
  -s [ --schema ] arg    Schema definition file path
  -p [ --prefix ] arg    Prefix to use for the generated C++ filenames
  -n [ --namespace ] arg C++ sub-namespace for the generated types
  --source-dir arg       Target path for the <prefix>Schema.cpp source file
  --header-dir arg       Target path for the <prefix>Schema.h header file
  --stubs                Unimplemented fields throw runtime exceptions instead
                         of compiler errors
  --no-introspection     Do not generate support for Introspection
```

A GraphQL query language parser in C++ with C and C++ APIs.

A GraphQL Client for.NET.

Basic example GraphQL client for.NET.

A straightforward Linq to GraphQL Client

README

Linq2GraphQL generates C# classes from the GraphQL schema and and togheter with the nuget package Linq2GraphQL.Client it makes it possible to query the server using Linq expressions.

A simple query that will get the first 10 orders with the primitive properties of orders and the connected customer

```
var orders = await sampleClient
    .Query
        .Orders(first: 10)
        .Include(e => e.Orders.Select(e => e.Customer))
        .Select(e => e.Orders)
        .ExecuteAsync();
```

An example mutation where we add a new customer and return the Customer Id.

```
var customerId = await sampleClient
    .Mutation
    .AddCustomer(new CustomerInput
    {
        CustomerId = Guid.NewGuid(),
        CustomerName = "New Customer",
        Status = CustomerStatus.Active
    })
    .Select(e=> e.CustomerId)
    .ExecuteAsync();
```

GraphQL client which supports generating queries from C# classes

Strawberry Shake is a open-source reactive GraphQL client for.NET

README

Strawberry Shake removes the complexity of state management and lets you interact with local and remote data through GraphQL.

You can use Strawberry Shake to:

- Generate a C# client from your GraphQL queries.
- Interact with local and remote data through GraphQL.
- Use reactive APIs to interact with your state.

```
client.GetHero
    .Watch(ExecutionStrategy.CacheFirst)
    .Subscribe(result =>
    {
        Console.WriteLine(result.Data.Name);
    })
```

ZeroQL is a open-source GraphQL client for C#

README

The ZeroQL is a high-performance C#-friendly GraphQL client. It supports Linq-like syntax, and doesn’t require Reflection.Emit or expressions. As a result, at runtime provides performance very close to a raw HTTP call.

You can use ZeroQL to:

- Generate a C# client from GraphQL schema.
- Generate and execute graphql queries from your C# code.
- Don’t require writing GraphQL manually.
- Supports.Net Core,.Net Framework, Xamarin, Unity apps.

```
var userId = 10;
var response = await qlClient.Query(q => q
    .User(userId, o => new
    {
        o.Id,
        o.FirstName,
        o.LastName
    }));
```

A GraphQL library for.NET Core. Easily expose you data model as a GraphQL API or bring together multiple data sources into a single GraphQL schema.

README

```
// expose an existing data model with ASP.NET & EF Core
public class Startup {
  public void ConfigureServices(IServiceCollection services)
  {
      services.AddDbContext<DemoContext>();
      // Auto build a schema from DemoContext. Alternatively you can build one from scratch
      services.AddGraphQLSchema<DemoContext>(options =>
      {
          // modify the schema (add/remove fields or types), add other services
      });
  }
 
  public void Configure(IApplicationBuilder app, DemoContext db)
  {
      app.UseRouting();
      app.UseEndpoints(endpoints =>
      {
          // defaults to /graphql endpoint
          endpoints.MapGraphQL<DemoContext>();
      });
  }
}
```

GraphQL for.NET

README

```
using System;
using System.Threading.Tasks;
using GraphQL;
using GraphQL.Types;
using GraphQL.SystemTextJson; // First add PackageReference to GraphQL.SystemTextJson
 
public class Program
{
  public static async Task Main(string[] args)
  {
    var schema = Schema.For(@"
      type Query {
        hello: String
      }
    ");
 
    var json = await schema.ExecuteAsync(_ =>
    {
      _.Query = "{ hello }";
      _.Root = new { Hello = "Hello World!" };
    });
 
    Console.WriteLine(json);
  }
}
```

Convert GraphQL to IQueryable

Hot Chocolate is an open-source GraphQL Server for.NET

README

Hot Chocolate takes the complexity away from building a fully-fledged GraphQL server and lets you focus on delivering the next big thing.

```
using Microsoft.AspNetCore;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
 
WebHost
    .CreateDefaultBuilder(args)
    .ConfigureServices(services =>
        services
            .AddGraphQLServer()
            .AddQueryType<Query>())
    .Configure(builder =>
        builder
            .UseRouting()
            .UseEndpoints(e => e.MapGraphQL()))
    .Build()
    .Run();
 
public class Query
{
    public Hero GetHero() => new Hero();
}
 
public class Hero
{
    public string Name => "Luke Skywalker";
}
```

A set of packages for implementing high-performant GraphQL servers in.NET. Faithful implementation of official 2018 Specification. Features batched execution support (aka Data Loader); support for custom scalars; HTTP server based on ASP.NET Core; parsed query cache; modular API construction (equivalent of schema stiching); full introspection support; runtime metrics and quotas.[Clojure](https://graphql.org/community/tools-and-libraries/?tags=clojure)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A GraphQL client implemented in Clojurescript with support for websockets.[Clojure](https://graphql.org/community/tools-and-libraries/?tags=clojure)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A set of reusable GraphQL components for Clojure conforming to the data structures given in [alumbra.spec](https://github.com/alumbra/alumbra.spec).

README

```
(require '[alumbra.core :as alumbra]
         '[claro.data :as data])
 
(def schema
  "type Person { name: String!, friends: [Person!]! }
   type QueryRoot { person(id: ID!): Person, me: Person! }
   schema { query: QueryRoot }")
 
(defrecord Person [id]
  data/Resolvable
  (resolve! [_ _]
    {:name    (str "Person #" id)
     :friends (map ->Person  (range (inc id) (+ id 3)))}))
 
(def QueryRoot
  {:person (map->Person {})
   :me     (map->Person {:id 0})})
 
(def app
  (alumbra/handler
    {:schema schema
     :query  QueryRoot}))
 
(defonce my-graphql-server
  (aleph.http/start-server #'app {:port 3000}))
```

```
$ curl -XPOST "http://0:3000" -H'Content-Type: application/json' -d'{
  "query": "{ me { name, friends { name } } }"
}'
{"data":{"me":{"name":"Person #0","friends":[{"name":"Person #1"},{"name":"Person #2"}]}}}
```[Clojure](https://graphql.org/community/tools-and-libraries/?tags=clojure)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Clojure library that provides a GraphQL implementation.

README

Code that executes a hello world GraphQL query with `graphql-clj`:

```
(def schema "type QueryRoot {
    hello: String
  }")
 
(defn resolver-fn [type-name field-name]
  (get-in {"QueryRoot" {"hello" (fn [context parent & rest]
                              "Hello world!")}}
          [type-name field-name]))
 
(require '[graphql-clj.executor :as executor])
 
(executor/execute nil schema resolver-fn "{ hello }")
```[Clojure](https://graphql.org/community/tools-and-libraries/?tags=clojure)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A full implementation of the GraphQL specification that aims to maintain external compliance with the specification.[D](https://graphql.org/community/tools-and-libraries/?tags=d)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A GraphQL implementation for the D Programming Language.[Elixir](https://graphql.org/community/tools-and-libraries/?tags=elixir)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Elixir GraphQL Client with HTTP and WebSocket support[Elixir](https://graphql.org/community/tools-and-libraries/?tags=elixir)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A GraphQL client for Elixir[Elixir](https://graphql.org/community/tools-and-libraries/?tags=elixir)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

GraphQL implementation for Elixir.[Elixir](https://graphql.org/community/tools-and-libraries/?tags=elixir)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

An Elixir implementation of Facebook's GraphQL.[Elm](https://graphql.org/community/tools-and-libraries/?tags=elm)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Library and command-line code generator to create type-safe Elm code for a GraphQL endpoint.[Erlang](https://graphql.org/community/tools-and-libraries/?tags=erlang)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

GraphQL implementation in Erlang.[Flutter](https://graphql.org/community/tools-and-libraries/?tags=flutter)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Ferry is a simple, powerful GraphQL Client for Flutter and Dart.[Flutter](https://graphql.org/community/tools-and-libraries/?tags=flutter)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A GraphQL client implementation in Flutter.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A truly type-safe Go GraphQL client.

README

genqlient is a Go library to easily generate type-safe code to query a GraphQL API. It takes advantage of the fact that both GraphQL and Go are typed languages to ensure at compile-time that your code is making a valid GraphQL query and using the result correctly, all with a minimum of boilerplate.

genqlient provides:

- Compile-time validation of GraphQL queries: never ship an invalid GraphQL query again!
- Type-safe response objects: genqlient generates the right type for each query, so you know the response will unmarshal correctly and never need to use `interface{}`.
- Production-readiness: genqlient is used in production at Khan Academy, where it supports millions of learners and teachers around the world.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A GraphQL Go client with Mutation, Query and Subscription support.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A GraphQL client implementation in Go.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

An elegant low-level HTTP client for GraphQL.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Go generate based graphql server library.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Easy to use, complete Go implementation of GraphQL. Simple and schema-less.

README

The purpose of Eggql is to make it as simple as possible to create a GraphQL server. You don’t need to create GraphQL schema (though you can view the schema that is created if interested). It is currently in beta release but is a complete implementation of a GraphQL server apart from subscriptions.

Just to be clear it supports all of these GraphQL features: arguments (including defaults), objects/lists/enums/input/interface/union types, aliases, fragments, variables, directives, mutations, inline fragments, descriptions, introspection and custom scalars.

Tests (jMeter) show that it is as fast or faster than other Go implementations for simple queries. We’re working on enhancements for performance including caching, data-loader, complexity-limits, etc.

To run an `eggql` hello world server just build and run this Go program:

```
package main

import "github.com/andrewwphillips/eggql"

func main() {
    http.Handle("/graphql", eggql.New(struct{ Message string }{Message: "hello, world"}))
    http.ListenAndServe(":80", nil)
}
```

This creates a root Query object with a single `message` field. To test it send a query with curl:

```
$ curl -XPOST -d '{"query": "{ message }"}' localhost:80/graphql
```

and you will get this response:

```
{
  "data": {
    "message": "hello, world"
  }
}
```[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Develop spec compliant GraphQL servers in Go.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

GraphQL server with a focus on ease of use.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

An implementation of GraphQL for Go / Golang.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Go/Golang library to help construct a graphql-go server supporting react-relay.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A GraphQL implementation with easy schema building, live queries, and batching.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A collection of tools for building GraphQL Servers, Gateways, Proxy Servers and Middleware in Go.

README

graphql-go-tools implements all basic blocks for building GraphQL Servers, Gateways and Proxy Servers. From lexing, parsing, validation, normalization, all the way up to query planning and execution.

It can also be understood as a GraphQL Compiler, with the ability to add your own backends. Just by implementing a few interfaces, you’re able to teach the compiler how to talk GraphQL to any backend.

The following backends are already implemented: [GraphQL](https://github.com/wundergraph/graphql-go-tools/tree/master/pkg/engine/datasource/graphql_datasource), with support for Apollo Federation / Supergraph. [Databases](https://github.com/wundergraph/wundergraph/tree/main/pkg/datasources/database): PostgreSQL, MySQL, SQLite, CockroachDB, MongoDB, SQLServer, [OpenAPI / REST](https://github.com/wundergraph/wundergraph/tree/main/pkg/datasources/oas) and [Kafka](https://github.com/wundergraph/graphql-go-tools/tree/master/pkg/engine/datasource/kafka_datasource).

To get a sense on how to implement a new backend, check out the [Static Data Source](https://github.com/wundergraph/graphql-go-tools/tree/master/pkg/engine/datasource/staticdatasource), as it’s the simplest one.

It’s used in production by many enterprises for multiple years now, battle tested and actively maintained.[Go](https://graphql.org/community/tools-and-libraries/?tags=go)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

An instant GraphQL to SQL compiler. Use as a standalone service or a Go library. Formerly super-graph.[Groovy](https://graphql.org/community/tools-and-libraries/?tags=groovy)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

An automatic GraphQL schema generator for GORM

README

**Core Library** - The GORM GraphQL library provides functionality to generate a GraphQL schema based on your GORM entities. In addition to mapping domain classes to a GraphQL schema, the core library also provides default implementations of “data fetchers” to query, update, and delete data through executions of the schema.

**Grails Plugin** - In a addition to the Core Library, the GORM GraphQL Grails Plugin:

- Provides a controller to receive and respond to GraphQL requests through HTTP, based on their guidelines.
- Generates the schema at startup with spring bean configuration to make it easy to extend.
- Includes a [GraphiQL](https://github.com/graphql/graphiql) browser enabled by default in development. The browser is accessible at /graphql/browser.
- Overrides the default data binder to use the data binding provided by Grails
- Provides a [trait](https://grails.github.io/gorm-graphql/latest/api/org/grails/gorm/graphql/plugin/testing/GraphQLSpec.html) to make integration testing of your GraphQL endpoints easier

See [the documentation](https://grails.github.io/gorm-graphql/latest/guide/index.html) for more information.[Groovy](https://graphql.org/community/tools-and-libraries/?tags=groovy)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

GQL is a Groove library for GraphQL[Haskell](https://graphql.org/community/tools-and-libraries/?tags=haskell)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A strongly-typed GraphQL client implementation in Haksell.[Haskell](https://graphql.org/community/tools-and-libraries/?tags=haskell)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Complete set of library tools to abstract relational database schemas with SQL, query with GraphQL, and return GraphQL results

README

One time setup: build schema, deploy as microservice or within server, query SQL database with GraphQL![Haskell](https://graphql.org/community/tools-and-libraries/?tags=haskell)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Haskell library for building GraphQL APIs.

README

Hello world example with `morpheus-graphql`:

```
# schema.gql
"""
A supernatural being considered divine and sacred
"""
type Deity {
  name: String!
  power: String @deprecated(reason: "no more supported")
}
type Query {
  deity(name: String! = "Morpheus"): Deity!
}
```

```
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE DuplicateRecordFields #-}
{-# LANGUAGE FlexibleContexts #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE NamedFieldPuns #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE TemplateHaskell #-}
{-# LANGUAGE TypeFamilies #-}
module API (api) where
import Data.ByteString.Lazy.Char8 (ByteString)
import Data.Morpheus (interpreter)
import Data.Morpheus.Document (importGQLDocument)
import Data.Morpheus.Types (RootResolver (..), Undefined (..))
import Data.Text (Text)
importGQLDocument "schema.gql"
rootResolver :: RootResolver IO () Query Undefined Undefined
rootResolver =
  RootResolver
    { queryResolver = Query {deity},
      mutationResolver = Undefined,
      subscriptionResolver = Undefined
    }
  where
    deity DeityArgs {name} =
      pure
        Deity
          { name = pure name,
            power = pure (Just "Shapeshifting")
          }
api :: ByteString -> IO ByteString
api = interpreter rootResolver
```

See [morpheus-graphql-examples](https://github.com/morpheusgraphql/morpheus-graphql) for more sophisticated APIs.[Haskell](https://graphql.org/community/tools-and-libraries/?tags=haskell)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Haskell library for building microservices (gRPC, HTTP) and GraphQL APIs.

README

Example implementation of a GraphQL server with type-level representation of the schema auto-generated:

```
{-# LANGUAGE DataKinds #-}
{-# LANGUAGE NamedFieldPuns #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE PartialTypeSignatures #-}
{-# LANGUAGE TypeApplications #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE TypeOperators #-}
 
-- imports omitted for brevity...
 
graphql "Library" "library.graphql" -- all the magic happens here! 🪄🎩
 
-- ... a bit more code...
 
libraryServer :: SqlBackend -> ServerT ObjectMapping i Library ServerErrorIO _
libraryServer conn =
  resolver
    ( object @"Book"
        ( field @"id" bookId,
          field @"title" bookTitle,
          field @"author" bookAuthor,
          field @"imageUrl" bookImage
        ),
      object @"Author"
        ( field @"id" authorId,
          field @"name" authorName,
          field @"books" authorBooks
        ),
      object @"Query"
        ( method @"authors" allAuthors,
          method @"books" allBooks
        ),
      object @"Mutation"
        ( method @"newAuthor" newAuthor,
          method @"newBook" newBook
        ),
      object @"Subscription"
        (method @"allBooks" allBooksConduit)
    )
  where
    bookId :: Entity Book -> ServerErrorIO Integer
    bookId (Entity (BookKey k) _) = pure $ toInteger k
    -- ... more resolvers...
```

See [our docs](https://higherkindness.io/mu-haskell/graphql/) for more information about how to build your own GraphQL server and [the library example](https://github.com/higherkindness/mu-graphql-example-elm) for a more end-to-end example that includes a client written in Elm!

A strongly-typed, caching GraphQL client for the JVM, Android, and Kotlin multiplatform.

README

Apollo Kotlin (formerly known as Apollo Android) is a GraphQL client with support for Android, Java8+, iOS and Kotlin multiplatform in general. It features:

- Java and Kotlin Multiplatform code generation
- Queries, Mutations and Subscriptions
- Reflection-free parsing
- Normalized cache
- Custom scalar types
- HTTP cache
- Auto Persisted Queries
- Query batching
- File uploads
- Espresso IdlingResource
- Fake models for tests
- AppSync and graphql-ws websockets
- GraphQL AST parser

A set of libraries for running GraphQL client and server in Kotlin.

README

GraphQL Kotlin provides a set of lightweight type-safe GraphQL HTTP clients. The library provides Ktor HTTP client and Spring WebClient based reference implementations as well as allows for custom implementations using other engines. Jackson and kotlinx-serialization type-safe data models are generated at build time by the provided Gradle and Maven plugins.

To generate Jackson models that will be used with GraphQL Kotlin Spring WebClient, add following to your Gradle build file:

```
// build.gradle.kts
import com.expediagroup.graphql.plugin.gradle.graphql
 
plugins {
    id("com.expediagroup.graphql") version $latestGraphQLKotlinVersion
}
 
dependencies {
  implementation("com.expediagroup:graphql-kotlin-spring-client:$latestGraphQLKotlinVersion")
}
 
graphql {
    client {
        // target GraphQL endpoint
        endpoint = "http://localhost:8080/graphql"
        // package for generated client code
        packageName = "com.example.generated"
    }
}
```

By default, GraphQL Kotlin plugins will look for query files under `src/main/resources`. Given `HelloWorldQuery.graphql` sample query:

```
query HelloWorldQuery {
  helloWorld
}
```

Plugin will generate classes that are simple POJOs implementing GraphQLClientRequest interface and represent a GraphQL request.

```
package com.example.generated
 
import com.expediagroup.graphql.client.types.GraphQLClientRequest
import kotlin.String
import kotlin.reflect.KClass
 
const val HELLO_WORLD_QUERY: String = "query HelloWorldQuery {\n    helloWorld\n}"
 
class HelloWorldQuery: GraphQLClientRequest<HelloWorldQuery.Result> {
    override val query: String = HELLO_WORLD_QUERY
 
    override val operationName: String = "HelloWorldQuery"
 
    override fun responseType(): KClass<HelloWorldQuery.Result> = HelloWorldQuery.Result::class
 
    data class Result(
        val helloWorld: String
    }
}
```

We can then execute our queries using target client.

```
package com.example.client
 
import com.expediagroup.graphql.client.spring.GraphQLWebClient
import com.expediagroup.graphql.generated.HelloWorldQuery
import kotlinx.coroutines.runBlocking
 
fun main() {
    val client = GraphQLWebClient(url = "http://localhost:8080/graphql")
    runBlocking {
        val helloWorldQuery = HelloWorldQuery()
        val result = client.execute(helloWorldQuery)
        println("hello world query result: ${result.data?.helloWorld}")
    }
}
```

See [graphql-kotlin client docs](https://opensource.expediagroup.com/graphql-kotlin/docs/client/client-overview) for additional details.

A GraphQL JVM Client designed for constructing queries from standard model definitions. By American Express.

A lightweight graphql calculation engine.

README

GraphQL Calculator is a lightweight graphql calculation engine, which is used to alter execution behavior of graphql query.

Here are some examples on how to use GraphQL Calculator on graphql query.

```
query basicMapValue($userIds: [Int]) {
  userInfoList(userIds: $userIds) {
    id
    age
    firstName
    lastName
    fullName: stringHolder @map(mapper: "firstName + lastName")
  }
}
 
query filterUserByAge($userId: [Int]) {
  userInfoList(userIds: $userId) @filter(predicate: "age>=18") {
    userId
    age
    firstName
    lastName
  }
}
 
query parseFetchedValueToAnotherFieldArgumentMap($itemIds: [Int]) {
  itemList(itemIds: $itemIds) {
    # save sellerId as List<Long> with unique name "sellerIdList"
    sellerId @fetchSource(name: "sellerIdList")
    name
    saleAmount
    salePrice
  }
 
  userInfoList(userIds: 1)
    # transform the argument of "userInfoList" named "userIds" according to expression "sellerIdList" and expression argument,
    # which mean replace userIds value by source named "sellerIdList"
    @argumentTransform(
      argumentName: "userIds"
      operateType: MAP
      expression: "sellerIdList"
      dependencySources: ["sellerIdList"]
    ) {
    userId
    name
    age
  }
}
```

See [graphql-calculator README](https://github.com/graphql-calculator/graphql-calculator) for more information.

GraphQL Spring Boot from GraphQL Java Kickstart

README

The GraphQL Spring Boot turns any Spring Boot application into a GraphQL Server

Started includes features such as:

- Use a schema-driven API with the help of [GraphQL Java Tools](https://github.com/graphql-java-kickstart/graphql-java-tools)
- Optionally choose to use an annotation driven schema with the help of [GraphQL-Java Annotations](https://github.com/Enigmatis/graphql-java-annotations)
- Embedded [GraphiQL](https://github.com/graphql/graphiql) tool for schema introspection and query debugging
- Embedded [GraphQL Playground](https://github.com/prisma/graphql-playground) tool for schema introspection and query debugging
- Embedded the [GraphQL Voyager](https://github.com/APIs-guru/graphql-voyager) tool to represent your GraphQL API as an interactive graph

See [GraphQL Java Kickstart Getting Started](https://www.graphql-java-kickstart.com/spring-boot/getting-started/) for how to get started.

A Java library for building GraphQL APIs.

README

See the [Getting Started tutorial](https://www.graphql-java.com/tutorials/getting-started-with-spring-boot) on the GraphQL Java website.

Code that executes a hello world GraphQL query with `graphql-java`:

```
import graphql.ExecutionResult;
import graphql.GraphQL;
import graphql.schema.GraphQLSchema;
import graphql.schema.StaticDataFetcher;
import graphql.schema.idl.RuntimeWiring;
import graphql.schema.idl.SchemaGenerator;
import graphql.schema.idl.SchemaParser;
import graphql.schema.idl.TypeDefinitionRegistry;
 
import static graphql.schema.idl.RuntimeWiring.newRuntimeWiring;
 
public class HelloWorld {
 
    public static void main(String[] args) {
        String schema = "type Query{hello: String}";
 
        SchemaParser schemaParser = new SchemaParser();
        TypeDefinitionRegistry typeDefinitionRegistry = schemaParser.parse(schema);
 
        RuntimeWiring runtimeWiring = newRuntimeWiring()
                .type("Query", builder -> builder.dataFetcher("hello", new StaticDataFetcher("world")))
                .build();
 
        SchemaGenerator schemaGenerator = new SchemaGenerator();
        GraphQLSchema graphQLSchema = schemaGenerator.makeExecutableSchema(typeDefinitionRegistry, runtimeWiring);
 
        GraphQL build = GraphQL.newGraphQL(graphQLSchema).build();
        ExecutionResult executionResult = build.execute("{hello}");
 
        System.out.println(executionResult.getData().toString());
        // Prints: {hello=world}
    }
}
```

See [the graphql-java docs](https://www.graphql-java.com/documentation/master/getting-started) for further information.

A set of libraries for running GraphQL client and server in Kotlin.

README

GraphQL Kotlin follows a code first approach for generating your GraphQL schemas. Given the similarities between Kotlin and GraphQL, such as the ability to define nullable/non-nullable types, a schema can be generated from Kotlin code without any separate schema specification. To create a reactive GraphQL web server add following dependency to your Gradle build file:

```
// build.gradle.kts
implementation("com.expediagroup", "graphql-kotlin-spring-server", latestVersion)
```

We also need to provide a list of supported packages that can be scanned for exposing your schema objects through reflections. Add following configuration to your `application.yml` file:

```
graphql:
  packages:
    - "com.your.package"
```

With the above configuration we can now create our schema. In order to expose your queries, mutations and/or subscriptions in the GraphQL schema you simply need to implement corresponding marker interface and they will be automatically picked up by `graphql-kotlin-spring-server` auto-configuration library.

```
@Component
class HelloWorldQuery : Query {
  fun helloWorld() = "Hello World!!!"
}
```

This will result in a reactive GraphQL web application with following schema:

```
type Query {
  helloWorld: String!
}
```

See [graphql-kotlin docs](https://expediagroup.github.io/graphql-kotlin/docs) for additial details.

A revolutionary ORM framework for both java and kotlin, it also provides specialized API for rapid development of Spring GraphQL-based applications.

README

**Introduce**
1. SpringBoot has introduced Spring GraphQL since 2.7. Jimmer provides specialized API for rapid development of Spring GraphQL-based applications.
2. Support two APIs: Java API & kotlin API.
3. Powerful and GraphQL friendly caching support.
4. Faster than other popular ORM solutions, please see the benchmark: [https://babyfish-ct.github.io/jimmer/docs/benchmark/](https://babyfish-ct.github.io/jimmer/docs/benchmark/)
5. More powerful than other popular ORM solutions.
	Three aspects should be considered in ORM design:
	a. Query. b. Update. c. Cache.
	Each aspect is aimed at object trees with arbitrary depth rather than simple objects. This distinctive design brings convenience unmatched by other popular solutions.
**Links**
- Youtube video: [https://www.youtube.com/watch?v=Rt5zNv0YR2E](https://www.youtube.com/watch?v=Rt5zNv0YR2E)
- Documentation: [https://babyfish-ct.github.io/jimmer/](https://babyfish-ct.github.io/jimmer/)
- Project Home: [https://github.com/babyfish-ct/jimmer](https://github.com/babyfish-ct/jimmer)
- GraphQL example for Java: [https://github.com/babyfish-ct/jimmer/tree/main/example/java/jimmer-sql-graphql](https://github.com/babyfish-ct/jimmer/tree/main/example/java/jimmer-sql-graphql)
- GraphQL example for Kotlin: [https://github.com/babyfish-ct/jimmer/tree/main/example/kotlin/jimmer-sql-graphql-kt](https://github.com/babyfish-ct/jimmer/tree/main/example/kotlin/jimmer-sql-graphql-kt)

KGraphQL is a pure Kotlin implementation of a code-first GraphQL server with focus on a rich and easy-to-use DSL that leverages existing code to set up the schema.

README

Here’s an example of how to create a simple schema based on a Kotlin data class plus a property resolver that gets applied onto your class:

```
data class Article(val id: Int, val text: String)
 
suspend fun main() {
    val schema = KGraphQL.schema {
        query("article") {
            resolver { id: Int?, text: String ->
                Article(id ?: -1, text)
            }
        }
        type<Article> {
            property("fullText") {
                resolver { article: Article ->
                    "${article.id}: ${article.text}"
                }
            }
        }
    }
 
    schema.execute("""
        {
            article(id: 5, text: "Hello World") {
                id
                fullText
            }
        }
    """.trimIndent()).let(::println)
 
    // {"data":{"article":{"id":5,"fullText":"5: Hello World"}}}
}
```

KGraphQL is using coroutines behind the scenes to provide great asynchronous performance.

See [KGraphQL docs](https://stuebingerb.github.io/KGraphQL/Installation/) for more in depth usage.

**Ktor Plugin**

KGraphQL has a Ktor plugin which gives you a fully functional GraphQL server with a single [install](https://ktor.io/docs/server-plugins.html#install) function call. The example below shows how to set up a GraphQL server within Ktor and it will give you a [GraphQL IDE](https://github.com/graphql/graphiql/tree/main) out of the box by entering `localhost:8080/graphql`.

```
fun Application.module() {
  install(GraphQL) {
    playground = true
    schema {
      query("hello") {
        resolver { -> "World!" }
      }
    }
  }
}
```

You can follow the [Ktor tutorial](https://stuebingerb.github.io/KGraphQL/Tutorials/ktor/) to set up a KGraphQL server with Ktor.

MP GraphQL is a code-first specification for building GraphQL applications. It uses annotations and design patterns similar to JAX-RS to enable rapid development.

README

MicroProfile GraphQL is a GraphQL server and client specification for building GraphQL applications. It’s unique annotation-based API approach enables rapid application development. Applications coded to the MP GraphQL APIs are portable, and can be deployed into Java server runtimes such as [Open Liberty](https://openliberty.io/), [Quarkus](https://quarkus.io/), [Helidon](https://helidon.io/) and [Wildfly](https://www.wildfly.org/). This means that your applications can make use of other [Jakarta](https://jakarta.ee/) and [MicroProfile](https://microprofile.io/) technologies.

MP GraphQL features include:

- Annotation-based APIs
- Integration with Jakarta CDI
- Type-safe and dynamic client APIs
- Exception handling
- Easy integration with Jakarta and MicroProfile technologies

Want to get started? Check out these resources:

- Learn how to [create and deploy a server side app in Open Liberty](https://openliberty.io/guides/microprofile-graphql.html).
- Learn how to [create a client application in Open Liberty](https://openliberty.io/guides/graphql-client.html).
- Learn how to [create and deploy a server side app in Quarkus](https://quarkus.io/guides/smallrye-graphql).
- Quick tutorial to [build a simple sample weather application](https://dzone.com/articles/have-it-your-way-with-microprofile-graphql).

Or these videos:

- [Integrating GraphQL and JPA](https://www.youtube.com/watch?v=RzrkjuA3LvU)
- [Writing Queryable APIs with MP GraphQL](https://www.youtube.com/watch?v=OOnpUeblVPM)

The DGS Framework (Domain Graph Service) is a GraphQL server framework for Spring Boot, developed by Netflix.

README

The DGS Framework (Domain Graph Service) is a GraphQL server framework for Spring Boot, developed by Netflix.

Features include:

- Annotation based Spring Boot programming model
- Test framework for writing query tests as unit tests
- Gradle Code Generation plugin to create types from schema
- Easy integration with GraphQL Federation
- Integration with Spring Security
- GraphQL subscriptions (WebSockets and SSE)
- File uploads
- Error handling
- Many extension points

See [DGS Framework Getting Started](https://netflix.github.io/dgs/getting-started/) for how to get started.

Spring for GraphQL provides support for Spring applications built on GraphQL Java.

README

Spring for GraphQL provides support for Spring applications built on [GraphQL Java](https://www.graphql-java.com/). See the official [Spring guide](https://spring.io/guides/gs/graphql-server/) for how to build a GraphQL service in 15 minutes.

- It is a joint collaboration between the GraphQL Java team and Spring engineering.
- Our shared philosophy is to provide as little opinion as we can while focusing on comprehensive support for a wide range of use cases.
- It aims to be the foundation for all Spring, GraphQL applications.

Features:

- backend handling of GraphQL requests over HTTP, WebSocket, and RSocket.
- An annotation-based programming model where @Controller components use annotations to declare handler methods with flexible method signatures to fetch the data for specific GraphQL fields. For example:

```
@Controller
public class GreetingController {
 
    @QueryMapping
    public String hello() {
        return "Hello, world!";
    }
 
}
```

- frontend support for executing GraphQL requests over HTTP, WebSocket, and RSocket.
- Dedicated support for testing GraphQL requests over HTTP, WebSocket, and RSocket, as well as for testing directly against a server.

To get started, check the Spring GraphQL starter on [https://start.spring.io](https://start.spring.io/) and the [samples](https://docs.spring.io/spring-graphql/docs/current/reference/html/#samples) in this repository.

Viaduct is a GraphQL-based system that provides a unified interface for accessing and interacting with any data source.

README

Viaduct is Airbnb’s open-source, data-oriented service mesh built around a single, highly connected central GraphQL schema. It provides a unified interface for accessing and interacting with any data source, and its engine runs in production at scale at Airbnb.

At the heart of Viaduct’s developer experience is re-entrancy: logic hosted on Viaduct composes with other logic hosted on Viaduct by issuing GraphQL fragments and queries. Re-entrancy is crucial for maintaining modularity in a large codebase and avoiding classic monolith hazards.

See the [Viaduct documentation](https://viaduct.dev/) to get started.

GraphQL Java Generator is a tool that generates Java code to speed up development for Client and Server of GraphQL APIs

README

- GraphQL Java client: it generates the Java classes that call the GraphQL endpoint, and the POJO that will contain the data returned by the server. The GraphQL endpoint can then be queried by using a simple call to a Java method (see sample below)
- GraphQL Java server: it is based on [graphql-java](https://github.com/graphql-java/graphql-java) (listed here above). It generates all the boilerplate code. You’ll only have to implement what’s specific to your server, which are the joins between the GraphQL types. GraphQL Java Generator is available as a [Maven Plugin](https://graphql-maven-plugin-project.graphql-java-generator.com/index.html). A Gradle plugin is coming soon. Please note that GraphQL Java Generator is an accelerator: the generated code doesn’t depend on any library specific to GraphQL Java Generator. So, it helps you to start building application based on graphql-java. Once the code is generated, you can decide to manually edit it as any standard java application, and get rid of GraphQL Java Generator. Of course you can, and should, according to us:), continue using GraphQL Java Generator when your project evolves.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A powerful JavaScript GraphQL client, designed to work well with React, React Native, Angular 2, or just plain JavaScript.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A JavaScript library for application development using cloud services, which supports GraphQL backend and React components for working with GraphQL data.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A simple JavaScript GraphQL client，Let the \*.gql file be used as a module through webpack loader.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

The No-GraphQL client for TypeScript.

README

GQty is a query builder, a query fetcher and a cache manager solution all-in-one.

You interact with your GraphQL endpoint via Proxy objects. Under the hood, GQty captures what is being read, checks cache validity, fetch missing contents and then updates the cache for you.

Start using GQty by simply running our interactive codegen:

```
# npm
npx @gqty/cli
 
# yarn
yarn dlx @gqty/cli
 
# pnpm
pnpm dlx @gqty/cli
```

GQty also provides framework specific integrations such as `@gqty/react` and `@gqty/solid`, which can be installed via our CLI.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

An all purpose GraphQL client with view layer integrations for multiple frameworks in just 1.6kb.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

An extensible GraphQL client with modules for react, caching, request parsing, web workers, websockets and more...

README

The example below installs and initializes the GraphQLBox client with a persisted cache and debugging enabled.

```
npm install @graphql-box/core @graphql-box/client @graphql-box/request-parser @graphql-box/cache-manager @graphql-box/debug-manager @graphql-box/fetch-manager @graphql-box/helpers @cachemap/core @cachemap/reaper @cachemap/indexed-db @cachemap/constants @cachemap/types
```

```
import Cachemap from "@cachemap/core"
import indexedDB from "@cachemap/indexed-db"
import reaper from "@cachemap/reaper"
import CacheManager from "@graphql-box/cache-manager"
import Client from "@graphql-box/client"
import DebugManager from "@graphql-box/debug-manager"
import FetchManager from "@graphql-box/fetch-manager"
import RequestParser from "@graphql-box/request-parser"
import introspection from "./introspection-query"
 
const requestManager = new FetchManager({
  apiUrl: "/api/graphql",
  batchRequests: true,
  logUrl: "/log/graphql",
})
 
const client = new Client({
  cacheManager: new CacheManager({
    cache: new Cachemap({
      name: "client-cache",
      reaper: reaper({ interval: 300000 }),
      store: indexedDB(/* configure */),
    }),
    cascadeCacheControl: true,
    typeCacheDirectives: {
      // Add any type specific cache control directives in the format:
      // TypeName: "public, max-age=3",
    },
  }),
  debugManager: new DebugManager({
    environment: "client",
    log: (message, data, logLevel) => {
      requestManager.log(message, data, logLevel)
    },
    name: "CLIENT",
    performance: self.performance,
  }),
  requestManager,
  requestParser: new RequestParser({ introspection }),
})
 
// Meanwhile... somewhere else in your code
 
const { data, errors } = await client.request(queryOrMutation)
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Minimal React hooks-first GraphQL client with a tiny bundle, SSR support and caching

README

- 🥇 First-class hooks API
- ⚖️ *Tiny* bundle: only 7.6kB (2.8 gzipped)
- 📄 Full SSR support: see [graphql-hooks-ssr](https://github.com/nearform/graphql-hooks/tree/master/packages/graphql-hooks-ssr)
- 🔌 Plugin Caching: see [graphql-hooks-memcache](https://github.com/nearform/graphql-hooks/tree/master/packages/graphql-hooks-memcache)
- 🔥 No more render props hell
- ⏳ Handle loading and error states with ease
**Quickstart**

```
npm install graphql-hooks
```

First you’ll need to create a client and wrap your app with the provider:

```
import { GraphQLClient, ClientContext } from "graphql-hooks"
 
const client = new GraphQLClient({
  url: "/graphql",
})
 
function App() {
  return (
    <ClientContext.Provider value={client}>
      {/* children */}
    </ClientContext.Provider>
  )
}
```

Now in your child components you can make use of `useQuery`:

```
import { useQuery } from "graphql-hooks"
 
const HOMEPAGE_QUERY = \`query HomePage($limit: Int) {
  users(limit: $limit) {
    id
    name
  }
}\`
 
function MyComponent() {
  const { loading, error, data } = useQuery(HOMEPAGE_QUERY, {
    variables: {
      limit: 10,
    },
  })
 
  if (loading) return "Loading..."
  if (error) return "Something Bad Happened"
 
  return (
    <ul>
      {data.users.map(({ id, name }) => (
        <li key={id}>{name}</li>
      ))}
    </ul>
  )
}
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Simple, pluggable, zero-dependency, GraphQL over HTTP spec compliant server, client and audit suite.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A simple and flexible JavaScript GraphQL client that works in all JavaScript environments (the browser, Node.js, and React Native) - basically a lightweight wrapper around `fetch`.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Zero-dependency, HTTP/1 safe, simple, GraphQL over Server-Sent Events Protocol server and client.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

GraphQL client for TypeScript, automatically infers the type of the returned data according to the strongly typed query request[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Coherent, zero-dependency, lazy, simple, GraphQL over WebSocket Protocol compliant server and client.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

curl for GraphQL with autocomplete, subscriptions and GraphiQL. Also a dead-simple universal javascript GraphQL client.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A simple JavaScript GraphQL client that works in all JavaScript environments (the browser, Node.js, and React Native).[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Tiny GraphQL client library using template strings.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Facebook's framework for building React applications that talk to a GraphQL backend.

README

Relay is a JavaScript framework for building data-driven React applications.

- **Declarative:** Never again communicate with your data store using an imperative API. Simply declare your data requirements using GraphQL and let Relay figure out how and when to fetch your data.
- **Colocation:** Queries live next to the views that rely on them, so you can easily reason about your app. Relay aggregates queries into efficient network requests to fetch only what you need.
- **Mutations:** Relay lets you mutate data on the client and server using GraphQL mutations, and offers automatic data consistency, optimistic updates, and error handling.

[See how to use Relay in your own project](https://relay.dev/docs/en/introduction-to-relay).[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A highly customizable and versatile GraphQL client with which you add on features like normalized caching as you grow.

README

`urql` is a GraphQL client that exposes a set of helpers for several frameworks. It’s built to be highly customisable and versatile so you can take it from getting started with your first GraphQL project all the way to building complex apps and experimenting with GraphQL clients.

- Currently supports React, React Native, Preact, Svelte, and Vue, and is supported by GraphQL Code Generator.
- Logical yet simple default behaviour and document caching, and normalized caching via `@urql/exchange-graphcache`
- Fully customizable behaviour via “exchanges” (addon packages)[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Describe your GraphQL operations with Zod schemas and use a single schema as the source of truth for the query string, the inferred TypeScript response type, and runtime validation of the data you get back.

README

zodql compiles a [Zod](https://zod.dev/) schema into a GraphQL query, sends it through the HTTP client of your choice, and validates the response against that same schema. Because a query is just a schema, the GraphQL query, the TypeScript type of the response, and the runtime validation applied to it all come from one place — there’s no separate query string to keep in sync with your types, and no codegen step to run.

Since a query is an ordinary runtime value, you can reshape it with Zod’s own combinators (`.pick()`, `.omit()`, `.extend()`, …) to adapt a shared schema to the fields a given screen needs, and you can enforce validation rules that a GraphQL schema can’t express — non-empty strings, emails, URLs, numeric ranges, and any other Zod refinement — rejecting non-conforming responses at parse time. It supports queries and mutations, named operations, typed variables, field arguments, aliases, nested selection sets, fragments (including inline fragments), and unions/interfaces, and has no hard dependency on a particular HTTP library.

Install it alongside Zod:

```
npm install @mattiasahlsen/zodql zod
```

Describe a query with a Zod schema, compile it to GraphQL, and execute it through a client built on any HTTP transport:

```
import { zodql, zodqlField, buildZodqlClient } from "@mattiasahlsen/zodql"
import { z } from "zod"
 
// Describe the query with a Zod schema
const userSchema = z.object({
  user: zodqlField()
    .withArguments({ id: "$userId" })
    .toSchema(
      z.object({
        id: z.string(),
        name: z.string(),
        email: z.string(),
      }),
    ),
})
 
// Compile it to a GraphQL query
const userQuery = zodql("query", userSchema)
  .defineVariables({ userId: { typeName: "ID!", schema: z.string() } })
  .compile()
 
// Create a client from any HTTP transport whose \`post\` resolves to \`{ response, json }\`
const client = buildZodqlClient({
  post: async (_url, data) => {
    const response = await fetch("https://api.example.com/graphql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return { response, json: () => response.json() }
  },
})
 
// Execute the query; the response is validated against the schema
const { parseResponse } = await client.request(userQuery, { userId: "123" })
const { data } = await parseResponse()
// data.user is typed as { id: string; name: string; email: string }
```

The compiled GraphQL query:

```
query ($userId: ID!) {
  user(id: $userId) {
    id
    name
    email
  }
}
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A GraphQL server from Apollo that works with any Node.js HTTP framework

README

To run a hello world server with Apollo Server:

```
npm install @apollo/server graphql
```

Then run `node server.js` with this code in `server.js`:

```
import { ApolloServer } from "@apollo/server"
import { startStandaloneServer } from "@apollo/server/standalone"
 
// The GraphQL schema
const typeDefs = \`#graphql
  type Query {
    hello: String
  }
\`
 
// A map of functions which return data for the schema.
const resolvers = {
  Query: {
    hello: () => "world",
  },
}
 
const server = new ApolloServer({
  typeDefs,
  resolvers,
})
 
const { url } = await startStandaloneServer(server)
console.log(\`🚀 Server ready at ${url}\`)
```

Apollo Server has a built in standalone HTTP server and middleware for Express, and has an framework integration API that supports all [Node.js HTTP server frameworks and serverless environments](https://www.apollographql.com/docs/apollo-server/integrations/integration-index) via community integrations.

Apollo Server has a [plugin API](https://www.apollographql.com/docs/apollo-server/integrations/plugins), integration with Apollo Studio, and performance and security features such as [caching](https://www.apollographql.com/docs/apollo-server/performance/caching/), [automatic persisted queries](https://www.apollographql.com/docs/apollo-server/performance/apq/), and [CSRF prevention](https://www.apollographql.com/docs/apollo-server/security/cors#preventing-cross-site-request-forgery-csrf).[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

An extensible GraphQL server with modules for caching, request parsing, debugging, subscriptions and more...

README

The example below installs and initializes the GraphQLBox server with a persisted cache and debugging enabled.

```
npm install @graphql-box/core @graphql-box/server @graphql-box/client @graphql-box/request-parser @graphql-box/cache-manager @graphql-box/debug-manager @graphql-box/execute @graphql-box/helpers @cachemap/core @cachemap/reaper @cachemap/redis @cachemap/constants @cachemap/types
```

```
import Cachemap from "@cachemap/core"
import redis from "@cachemap/redis"
import reaper from "@cachemap/reaper"
import CacheManager from "@graphql-box/cache-manager"
import Client from "@graphql-box/client"
import DebugManager from "@graphql-box/debug-manager"
import Execute from "@graphql-box/execute"
import RequestParser from "@graphql-box/request-parser"
import Server from "@graphql-box/server"
import { makeExecutableSchema } from "@graphql-tools/schema"
import { performance } from "perf_hooks"
import { schemaResolvers, schemaTypeDefs } from "./schema"
import logger from "./logger"
 
const schema = makeExecutableSchema({
  typeDefs: schemaTypeDefs,
  resolvers: schemaResolvers,
})
 
const server = new Server({
  client: new Client({
    cacheManager: new CacheManager({
      cache: new Cachemap({
        name: "server-cache",
        reaper: reaper({ interval: 300000 }),
        store: redis(/* configure */),
      }),
      cascadeCacheControl: true,
      typeCacheDirectives: {
        // Add any type specific cache control directives in the format:
        // TypeName: "public, max-age=3",
      },
    }),
    debugManager: new DebugManager({
      environment: "server",
      log: (...args) => {
        logger.log(...args)
      },
      name: "SERVER",
      performance,
    }),
    requestManager: new Execute({ schema }),
    requestParser: new RequestParser({ schema }),
  }),
})
 
// Meanwhile... somewhere else in your code
 
app.use("api/graphql", graphqlServer.request())
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Simple, pluggable, zero-dependency, GraphQL over HTTP spec compliant server, client and audit suite.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

The reference implementation of the GraphQL specification, designed for running GraphQL in a Node.js environment.

README

To run a `GraphQL.js` hello world script from the command line:

```
npm install graphql
```

Then run `node hello.js` with this code in `hello.js`:

```
var { graphql, buildSchema } = require("graphql")
 
var schema = buildSchema(\`
  type Query {
    hello: String
  }
\`)
 
var rootValue = { hello: () => "Hello world!" }
 
var source = "{ hello }"
 
graphql({ schema, source, rootValue }).then(response => {
  console.log(response)
})
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Zero-dependency, HTTP/1 safe, simple, GraphQL over Server-Sent Events Protocol server and client.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Coherent, zero-dependency, lazy, simple, GraphQL over WebSocket Protocol compliant server and client.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

GraphQL Yoga is a batteries-included cross-platform GraphQL over HTTP spec-compliant GraphQL Server using Envelop and GraphQL Tools.

README

- Built around the Fetch API `Request` & `Response` objects
- GraphQL over HTTP compliant
- Extensible GraphQL Engine powered by Envelop
- GraphQL Subscriptions over HTTP
- Handle file uploads with GraphQL
- Integrates with AWS Lambda, Cloudflare Workers, Deno, Express, Next.js, SvelteKit, and more.

To run a hello world server with graphql-yoga:

```
npm install graphql-yoga graphql
```

Then create a server using the `createServer` import:

```
import { createServer } from "http"
import { createSchema, createYoga } from "graphql-yoga"
 
createServer(
  createYoga({
    schema: createSchema({
      typeDefs: /* GraphQL */ \`
        type Query {
          hello: String
        }
      \`,
      resolvers: {
        Query: {
          hello: () => "Hello Hello Hello",
        },
      },
    }),
  }),
).listen(4000, () => {
  console.info("GraphQL Yoga is listening on http://localhost:4000/graphql")
})
```

Depending on your deployment target, you may need to use an additional library. See the [documentation](https://www.graphql-yoga.com/docs) for further details.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Mercurius is a flexible and extendible GraphQL adapter for Fastify, a blazing-fast web framework with the least overhead and a powerful plugin architecture.

README

To run an hello world script with `mercurius`:

```
npm install fastify mercurius
```

Then run `node app.js` with this code in `app.js`:

```
const Fastify = require("fastify")
const mercurius = require("mercurius")
 
const schema = \`
  type Query {
    hello(name: String): String!
  }
\`
 
const resolvers = {
  Query: {
    hello: async (_, { name }) => \`hello ${name || "world"}\`,
  },
}
 
const app = Fastify()
app.register(mercurius, {
  schema,
  resolvers,
})
 
app.listen(3000)
 
// Call IT!
// curl 'http://localhost:3000/graphql' \
//  -H 'content-type: application/json' \
//  --data-raw '{"query":"{ hello(name:\"Marcurius\") }" }'
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A code-first framework for GraphQL API development, where your schema reflects your functionality. Run `npm create pylon@latest` to get started.

README

1. **Create**

```
npm create pylon@latest
```

2. **Develop**

Example service:

```
import { app } from "@getcronit/pylon"
 
class User {
  name: string
  email: string
  constructor(name: string, email: string) {
    this.name = name
    this.email = email
  }
}
 
const users = [
  new User("Alice", "[email protected]"),
  new User("Bob", "[email protected]"),
  new User("Charlie", "[email protected]"),
]
 
export const graphql = {
  Query: {
    users,
    user: (name: string) => {
      return users.find(user => user.name === name)
    },
  },
  Mutation: {
    addUser: (name: string, email: string) => {
      const user = new User(name, email)
      users.push(user)
      return user
    },
  },
}
 
export default app
```

3. **Query**

```
query User {
  user(name: "Alice") {
    name
    email
  }
}
 
query Users {
  users {
    name
    email
  }
}
 
mutation AddUser {
  addUser(name: "Corina", email: "[email protected]") {
    name
    email
  }
}
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

Browse Any Graph - A user-friendly viewer for any GraphQL service

README

**Brangr - *Br* owse *An* y *Gr* aph**

- Brangr is a simple, unique tool that any web server can host to provide a user-friendly browser/viewer for any GraphQL service (or many).
- Brangr formats GraphQL results attractively, via a selection of user-configurable layouts. It lets users extract the generated HTML, and its source JSON. It provides a clever schema browser. It has built-in docs.
- Brangr enables sites hosting it to present users with a collection of pre-fab GraphQL requests, which they can edit if desired, and let them create their own requests. And it allows sites to define custom CSS styling for all aspects of the formatted results.
- Try it at the [**public Brangr site**](https://mnmnotmail.org/bgr/brangr.html).

**Example**

```
query {
  heroes(_layout: { type: table }) { # _layout arg not sent to service
    first
    last
  }
}
```

Brangr renders the above query as follows (though not in a quote block):

> heroes...
> 
> | First | Last |
> | --- | --- |
> | Arthur | Dent |
> | Ford | Prefect |
> | Zaphod | Beeblebrox |[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

A plugin based schema builder for creating code-first GraphQL schemas in typescript

README

GiraphQL makes writing type-safe schemas simple, and works without a code generator, build process, or extensive manual type definitions.

```
import { ApolloServer } from "apollo-server"
import SchemaBuilder from "@giraphql/core"
 
const builder = new SchemaBuilder({})
 
builder.queryType({
  fields: t => ({
    hello: t.string({
      args: {
        name: t.arg.string({}),
      },
      resolve: (parent, { name }) => \`hello, ${name || "World"}\`,
    }),
  }),
})
 
new ApolloServer({
  schema: builder.toSchema({}),
}).listen(3000)
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

An interactive in-browser GraphQL IDE.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

The missing GraphQL security layer for Apollo GraphQL and Yoga / Envelop servers.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

A command line tool for common GraphQL development workflows.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

GraphQL code generator with flexible support for custom plugins and templates like Typescript (frontend and backend), React Hooks, resolvers signatures and more.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

One configuration for all your GraphQL tools (supported by most tools, editors & IDEs).[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

GraphQL-ESLint integrates GraphQL AST in the ESLint core (as a parser).[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

Simple, pluggable, zero-dependency, GraphQL over HTTP spec compliant server, client and audit suite.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

Compare schemas, validate documents, find breaking changes, find similar types, schema coverage, and more.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

An interface for building GraphQL language services for IDEs (diagnostics, autocomplete etc).[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

Real-Time with GraphQL for any GraphQL schema or transport.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

GraphQL Mesh allows you to use GraphQL query language to access data in remote APIs that don't run GraphQL (and also ones that do run GraphQL). It can be used as a gateway to other services, or run as a local GraphQL schema that aggregates data from remote APIs.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

Split up your GraphQL resolvers in middleware functions.

README

GraphQL Middleware is a schema wrapper which allows you to manage additional functionality across multiple resolvers efficiently.

**Features**

💡 Easy to use: An intuitive, yet familiar API that you will pick up in a second. 💪 Powerful: Allows complete control over your resolvers (Before, After). 🌈 Compatible: Works with any GraphQL Schema.

**Example**

```
const { ApolloServer } = require("apollo-server")
const { makeExecutableSchema } = require("@graphql-tools/schema")
 
const typeDefs = \`
type Query {
  hello(name: String): String
  bye(name: String): String
}
\`
const resolvers = {
  Query: {
    hello: (root, args, context, info) => {
      console.log(\`3. resolver: hello\`)
      return \`Hello ${args.name ? args.name : "world"}!\`
    },
    bye: (root, args, context, info) => {
      console.log(\`3. resolver: bye\`)
      return \`Bye ${args.name ? args.name : "world"}!\`
    },
  },
}
 
const logInput = async (resolve, root, args, context, info) => {
  console.log(\`1. logInput: ${JSON.stringify(args)}\`)
  const result = await resolve(root, args, context, info)
  console.log(\`5. logInput\`)
  return result
}
 
const logResult = async (resolve, root, args, context, info) => {
  console.log(\`2. logResult\`)
  const result = await resolve(root, args, context, info)
  console.log(\`4. logResult: ${JSON.stringify(result)}\`)
  return result
}
 
const schema = makeExecutableSchema({ typeDefs, resolvers })
 
const schemaWithMiddleware = applyMiddleware(schema, logInput, logResult)
 
const server = new ApolloServer({
  schema: schemaWithMiddleware,
})
 
await server.listen({ port: 8008 })
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

GraphQL Modules lets you separate your backend implementation to small, reusable, easy-to-implement and easy-to-test pieces.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

A library of custom GraphQL scalar types for creating precise, type-safe GraphQL schemas.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

A GraphQL tool to ease the creation of permission layer.

README

GraphQL Shield helps you create a permission layer for your application. Using an intuitive rule-API, you’ll gain the power of the shield engine on every request and reduce the load time of every request with smart caching. This way you can make sure your application will remain quick, and no internal data will be exposed.

```
import { rule, shield, and, or, not } from "graphql-shield"
 
// Rules
 
const isAuthenticated = rule({ cache: "contextual" })(async (
  parent,
  args,
  ctx,
  info,
) => {
  return ctx.user !== null
})
 
const isAdmin = rule({ cache: "contextual" })(async (
  parent,
  args,
  ctx,
  info,
) => {
  return ctx.user.role === "admin"
})
 
const isEditor = rule({ cache: "contextual" })(async (
  parent,
  args,
  ctx,
  info,
) => {
  return ctx.user.role === "editor"
})
 
// Permissions
 
const permissions = shield({
  Query: {
    frontPage: not(isAuthenticated),
    fruits: and(isAuthenticated, or(isAdmin, isEditor)),
    customers: and(isAuthenticated, isAdmin),
  },
  Mutation: {
    addFruitToBasket: isAuthenticated,
  },
  Fruit: isAuthenticated,
  Customer: isAdmin,
})
 
// Server
 
const server = new GraphQLServer({
  typeDefs,
  resolvers,
  middlewares: [permissions],
  context: req => ({
    ...req,
    user: getUser(req),
  }),
})
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

A set of utils for faster development of GraphQL tools (Schema and documents loading, Schema merging and more).[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

Implementation-first GraphQL for TypeScript. Annotate your existing TypeScript code with docblock tags and Grats statically extracts a GraphQL schema from it.

README

Grats takes an [implementation-first](https://jordaneldredge.com/implementation-first/) approach to building GraphQL servers in TypeScript. Instead of defining your schema in SDL or with a schema builder API and then wiring resolvers up to it, you write ordinary TypeScript functions, classes, and types, and mark the parts you want to expose with docblock tags like `/** @gqlType */` and `/** @gqlField */`. At build time Grats statically analyzes your code — using the TypeScript compiler’s own types, so no runtime reflection or decorators are involved — and derives both a `schema.graphql` file and an executable `GraphQLSchema`.

Because the schema is derived from your implementation, the two can’t drift apart: renaming a field, changing an argument, or making a return type nullable updates the schema automatically, and anything Grats can’t express as valid GraphQL is reported as a compile-time error with a pointer to the offending line. A companion TypeScript plugin surfaces those errors directly in your editor.

Annotate your types and resolvers:

```
/** @gqlType */
type User = {
  /** @gqlField */
  name: string
}
 
/** @gqlField */
export function greeting(user: User, salutation: string): string {
  return \`${salutation}, ${user.name}!\`
}
 
/** @gqlQueryField */
export function me(): User {
  return { name: "Alice" }
}
```

Then run `npx grats` to extract the schema:

```
type Query {
  me: User
}
 
type User {
  name: String
  greeting(salutation: String!): String
}
```

The generated module also exports the executable schema, which you can hand to any `graphql-js` -based server:

```
import { createYoga } from "graphql-yoga"
import { createServer } from "node:http"
import { getSchema } from "./schema"
 
createServer(createYoga({ schema: getSchema() })).listen(4000)
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

A library to query and manipulate GraphQL Introspection Query results.

README

Microfiber is a JavaScript library that allows:

- Digging through your Introspection Query Results for a specific Query, Mutation, Type, Field, Argument or Subscription.
- Removing a specific Query, Mutation, Type, Field/InputField, Argument or Subscription from your Introspection Query Results.
- Removing Queries, Mutations, Fields/InputFields or Arguments that refer to Type that does not exist in - or has been removed from - your Introspection Query Results.

```
npm install microfiber
# OR
yarn add microfiber
```

Then in JS:

```
import { Microfiber } from "microfiber"
 
const introspectionQueryResults = {
  // ...
}
 
const microfiber = new Microfiber(introspectionQueryResults)
 
// ...do some things to your schema with \`microfiber\`
 
const cleanedIntrospectonQueryResults = microfiber.getResponse()
```[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

builds a powerful, extensible and performant GraphQL API from a PostgreSQL schema in seconds; saving you weeks if not months of development time.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

Generate REST API from your GraphQL API.[JavaScript](https://graphql.org/community/tools-and-libraries/?tags=javascript)

[

Tools

](https://graphql.org/community/tools-and-libraries/?tags=tools)

SpectaQL generates static HTML documentation from a GraphQL schema.

README

SpectaQL is a Node.js library that generates static documentation for a GraphQL schema using a variety of options:

- From a live endpoint using the introspection query.
- From a file containing an introspection query result.
- From a file, files or glob leading to the schema definitions in SDL.

Out of the box, SpectaQL generates a single 3-column HTML page and lets you choose between a couple built-in themes. A main goal of the project is to be easily and extremely customizable—it is themeable and just about everything can be overridden or customized.

```
npm install --dev spectaql
# OR
yarn add -D spectaql
 
# Then generate your docs
npm run spectaql my-config.yml
# OR
yarn spectaql my-config.yml
```[Julia](https://graphql.org/community/tools-and-libraries/?tags=julia)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A Julia GraphQL server implementation.[Julia](https://graphql.org/community/tools-and-libraries/?tags=julia)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A Julia GraphQL client for seamless integration with a GraphQL server

README

- **Querying**, **mutating** and **subscribing** without manual writing of query strings (unless you want to!)
- Deserializing responses directly into Julia types
- **Construction of Julia types** from GraphQL objects
- Using **introspection** to help with querying
**Quickstart**

Install with Julia’s package manager

```
using Pkg; Pkg.add("GraphQLClient")
using GraphQLClient
```

Connect to a server

```
client = Client("https://countries.trevorblades.com")
```

Build a Julia type from a GraphQL object

```
Country = GraphQLClient.introspect_object(client, "Country")
```

And query the server, deserializing the response into this new type

```
response = query(client, "countries", Vector{Country}, output_fields="name")
```

Alternatively write the query string manually

```
query_string = """
    {
    countries{
        name
    }
}"""
 
response = GraphQLClient.execute(client, query_string)
```

GraphQL server library for OCaml and Reason[Perl](https://graphql.org/community/tools-and-libraries/?tags=perl)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Perl port of GraphQL reference implementation

README

- [MetaCPAN documentation](https://metacpan.org/pod/GraphQL)
	- [Mojolicious-Plugin-GraphQL](https://github.com/graphql-perl/Mojolicious-Plugin-GraphQL) - connect your GraphQL service to a Mojolicious app
		- [GraphQL-Plugin-Convert-DBIC](https://github.com/graphql-perl/GraphQL-Plugin-Convert-DBIC) - automatically connect your DBIx::Class schema to GraphQL
		- [GraphQL-Plugin-Convert-OpenAPI](https://github.com/graphql-perl/GraphQL-Plugin-Convert-OpenAPI) - automatically connect any OpenAPI service (either local Mojolicious one, or remote) to GraphQL[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

API Platform is a fully-featured, flexible and extensible API framework built on top of Symfony.

README

The following class is enough to create both a Relay-compatible GraphQL server and a hypermedia API supporting modern REST formats (JSON-LD, JSONAPI…):

```
<?php
 
namespace AppEntity;
 
use ApiPlatformCoreAnnotationApiResource;
use DoctrineORMMapping as ORM;
 
/**
 * Greet someone!
 *
 * @ApiResource
 * @ORMEntity
 */
class Greeting
{
    /**
     * @ORMId
     * @ORMColumn(type="guid")
     */
    public $id;
 
    /**
     * @var string Your nice message
     *
     * @ORMColumn
     */
    public $hello;
}
```

Other API Platform features include data validation, authentication, authorization, deprecations, cache and GraphiQL integration.[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Interact with all your data in WordPress[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A GraphQL implementation for modern PHP. Includes features from latest draft, middleware directives and modules with extra functionality.

README

GraPHPinator is feature complete PHP implementation of GraphQL server. Its job is transformation of query string into resolved Json result for a given Schema.

- Aims to be compliant with the latest draft of GraphQL specification.
- Fully typesafe, and therefore minimum required PHP version is 8.0. Sacrafices a tiny bit of convenience for huge amount of clarity and safety - no random configuration `array` s, no mixed types, no variable function arguments - this library doesnt try to save you from verbosity, but makes sure you always know what you’ve got.
- Code first.
- Flexible. Easy to extend with extra functionality using Modules or middleware Directives.
- Includes some opt-in extensions which are out of scope of official specs:
	- [Printer](https://github.com/infinityloop-dev/graphpinator-printer) - Schema printing for GraPHPinator typesystem.
		- [Extra types](https://github.com/infinityloop-dev/graphpinator-extra-types) - Some useful and commonly used types, both scalar or composite.
		- [Constraint directives](https://github.com/infinityloop-dev/graphpinator-constraint-directives) - Typesystem directives to declare additional validation on top of GraphQL typesystem.
		- [Where directives](https://github.com/infinityloop-dev/graphpinator-where-directives) - Executable directives to filter values in lists.
		- File upload using [multipart-formdata](https://github.com/jaydenseric/graphql-multipart-request-spec) specs (currently bundled).
		- [Query cost limit module](https://github.com/infinityloop-dev/graphpinator-query-cost) - Modules to limit query cost by restricting maximum depth or number of nodes.
- Project is composed from multiple smaller packages, which may be used standalone:
	- [Tokenizer](https://github.com/infinityloop-dev/graphpinator-tokenizer) - Lexical analyzer of GraphQL document.
		- [Parser](https://github.com/infinityloop-dev/graphpinator-parser) - Syntactic analyzer of GraphQL document.[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Easily build your GraphQL schema for webonyx/graphql-php using PHP attributes instead of large configuration arrays.

README

Easily build your GraphQL schema for `webonyx/graphql-php` using PHP attributes instead of large configuration arrays.

A simple example:

```
use Jerowork\GraphqlAttributeSchema\Attribute\Enum;
use Jerowork\GraphqlAttributeSchema\Attribute\Field;
use Jerowork\GraphqlAttributeSchema\Attribute\InputType;
use Jerowork\GraphqlAttributeSchema\Attribute\Mutation;
use Jerowork\GraphqlAttributeSchema\Attribute\Query;
use Jerowork\GraphqlAttributeSchema\Attribute\Type;
 
final readonly class CreateUserMutation
{
    #[Mutation]
    public function createUser(CreateUserInputType $input): User
    {
        // Business logic to create a user
    }
}
 
final readonly class UserQuery
{
    #[Query(description: 'Get a user')]
    public function user(int $userid): User
    {
        // Fetch and return user data
    }
}
 
#[InputType]
final readonly class CreateUserInputType
{
    public function __construct(
        #[Field]
        public int $userId,
        #[Field]
        public string $name,
        #[Field(name: 'phoneNumber')]
        public ?string $phone,
    ) {}
}
 
#[Type]
final readonly class User
{
    // Define fields as class properties
    public function __construct(
        #[Field]
        public int $userId,
        #[Field]
        public string $name,
        public ?string $phone,
        #[Field(description: 'The status of the user')]
        public UserStatusType $status,
    ) {}
 
    // Define fields with methods for additional logic
    #[Field]
    public function getPhoneNumber(): string
    {
        return sprintf('+31%s', $this->phone);
    }
}
 
#[Enum(description: 'The status of the user')]
enum UserStatusType: string
{
    case Created = 'CREATED';
    case Removed = 'REMOVED';
}
```

This will result in the following GraphQL schema:

```
type Mutation {
  createUser(input: CreateUserInput!): User!
}
 
type Query {
  user(userId: Int!): User!
}
 
input CreateUserInput {
  userId: Int!
  name: String!
  phoneNumber: String
}
 
type User {
  userId: Int!
  name: String!
  status: UserStatus!
  phoneNumber: String
}
 
enum UserStatus {
  CREATED
  REMOVED
}
```

Available attributes: `Mutation`, `Query`, `Type`, `InterfaceType`, `InputType`, `Enum`, `EnumValue`, `Field`, `Arg`, `Autowire`, `Scalar`, `Cursor`[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A PHP port of GraphQL reference implementation[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A library to help construct a graphql-php server supporting react-relay.[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A GraphQL server for Symfony[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

GraphQLite is a library that offers an annotations-based syntax for GraphQL schema definition.

README

It is framework agnostic with bindings available for Symfony and Laravel. This code declares a “product” query and a “Product” Type:

```
class ProductController
{
    /**
     * @Query()
     */
    public function product(string $id): Product
    {
        // Some code that looks for a product and returns it.
    }
}
 
/**
 * @Type()
 */
class Product
{
    /**
     * @Field()
     */
    public function getName(): string
    {
        return $this->name;
    }
    // ...
}
```

Other GraphQLite features include validation, security, error handling, loading via data-loader pattern…[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A GraphQL server for Laravel[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A PHP GraphQL Framework.[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Use GraphQL to define your Domain Model for CQRS/ES and let serge generate code to handle GraphQL requests.[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Siler is a PHP library powered with high-level abstractions to work with GraphQL.

README

To run a Siler hello world script:

```
type Query {
  hello: String
}
```

```
<?php
declare(strict_types=1);
require_once '/path/to/vendor/autoload.php';
 
use SilerDiactoros;
use SilerGraphql;
use SilerHttp;
 
$typeDefs = file_get_contents(__DIR__.'/schema.graphql');
$resolvers = [
    'Query' => [
        'hello' => 'world',
    ],
];
$schema = Graphqlschema($typeDefs, $resolvers);
 
echo "Server running at http://127.0.0.1:8080";
 
Httpserver(Graphqlpsr7($schema), function (Throwable $err) {
    var_dump($err);
    return Diactorosjson([
        'error'   => true,
        'message' => $err->getMessage(),
    ]);
})()->run();
```

It also provides functionality for the construction of a WebSocket Subscriptions Server based on how Apollo works.[PHP](https://graphql.org/community/tools-and-libraries/?tags=php)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A free, open-source WordPress plugin that provides an extendable GraphQL schema and API for any WordPress site[PowerShell](https://graphql.org/community/tools-and-libraries/?tags=powershell)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A PowerShell module for querying and mutating GraphQL endpoints.

README

PSGraphQL is a PowerShell module for working with GraphQL endpoints from scripts, shells, and automation workflows. It provides commands for sending GraphQL queries and mutations, passing variables, setting headers, and returning either PowerShell objects or raw JSON.

Install it from the PowerShell Gallery:

```
Install-Module -Name PSGraphQL -Scope CurrentUser
```

Run a simple GraphQL query:

```
$uri = "https://mytargetserver/v1/graphql"
 
$query = @'
query {
  users {
    id
    name
  }
}
'@
 
Invoke-GraphQLQuery -Uri $uri -Query $query
```

PSGraphQL can also send mutations, include operation names and variables, use custom headers for authentication, and read GraphQL queries from files.[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Generate fully typed Python GraphQL client from any schema and queries.

README

Install Ariadne Codegen:

```
$ pip install ariadne-codegen
```

Create `queries.graphql` file:

```
mutation CreateToken($username: String!, $password: String!) {
  createToken(username: $username, password: $password) {
    token
    errors {
      field
      message
    }
  }
}
```

Add `[ariadne-codegen]` section to your `pyproject.toml`:

```
[ariadne-codegen]
queries_path = "queries.graphql"
remote_schema_url = "http://example.com/graphql/"
```

Generate client:

```
$ ariadne-codegen
```

And use it in your Python projects:

```
import asyncio
from graphql_client import Client
 
 
async def create_token_gql():
    client = Client("http://example.com/graphql/")
    result = await client.create_token(username="Admin", password="Example123")
 
    if result.errors:
        error = result.errors[0]
        raise ValidationError({error.field: error.message})
 
    return result.token
 
asyncio.run(create_token_gql())
```[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A GraphQL client in Python.[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Complete GraphQL query string generation for python.

README

**graphql\_query** is complete GraphQL query string builder for python. With **graphql\_query** you can The documentation for **graphql\_query** can be found at [https://denisart.github.io/graphql-query](https://denisart.github.io/graphql-query).

```
$ pip install graphql_query
```

Code for the simple query

```
{
  hero {
    name
  }
}
```

it is

```
from graphql_query import Operation, Query
 
hero = Query(name="hero", fields=["name"])
operation = Operation(type="query", queries=[hero])
 
print(operation.render())
"""
query {
  hero {
    name
  }
}
"""
```

For generation of the following query

```
query Hero($episode: Episode, $withFriends: Boolean!) {
  hero(episode: $episode) {
    name
    friends @include(if: $withFriends) {
      name
    }
  }
}
```

we have

```
from graphql_query import Argument, Directive, Field, Operation, Query, Variable
 
episode = Variable(name="episode", type="Episode")
withFriends = Variable(name="withFriends", type="Boolean!")
 
arg_episode = Argument(name="episode", value=episode)
arg_if = Argument(name="if", value=withFriends)
 
hero = Query(
    name="hero",
    arguments=[arg_episode],
    fields=[
        "name",
        Field(
            name="friends",
            fields=["name"],
            directives=[Directive(name="include", arguments=[arg_if])]
        )
    ]
)
operation = Operation(
    type="query",
    name="Hero",
    variables=[episode, withFriends],
    queries=[hero]
)
print(operation.render())
"""
query Hero(
  $episode: Episode
  $withFriends: Boolean!
) {
  hero(
    episode: $episode
  ) {
    name
    friends @include(
      if: $withFriends
    ) {
      name
    }
  }
}
"""
```[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Simple GraphQL client for Python 2.7+.[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Non intrusive python GraphQL client wrapped around pydantic.

README

GraphQL client library, wrapped around pydantic classes for type validation, provides a safe and simple way to query data from a GraphQL API.

Features:

- python objects to valid GraphQL string
- scalar query responses
- type-safety
**Install**

```
pip3 install pydantic-graphql
```[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A fast and modern graphql client designed with simplicity in mind.

README

Here’s an example of a qlient hello world.

first install the library:

```
pip install qlient
```

Create a `swapi_client_example.py` file with this content:

```
from qlient.http import HTTPClient, GraphQLResponse
 
client = HTTPClient("https://swapi-graphql.netlify.app/.netlify/functions/index")
 
res: GraphQLResponse = client.query.film(
    # swapi graphql input fields
    id="ZmlsbXM6MQ==",
 
    # qlient specific
    _fields=["id", "title", "episodeID"]
)
 
print(res.request.query)  # query film($id: ID) { film(id: $id) { id title episodeID } }
print(res.request.variables)  # {'id': 'ZmlsbXM6MQ=='}
print(res.data)  # {'film': {'id': 'ZmlsbXM6MQ==', 'title': 'A New Hope', 'episodeID': 4}}
```

Close the file and run it using python:

```
python swapi_client_example.py
```[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A simple Python GraphQL client. Supports generating code generation for types defined in a GraphQL schema.[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Ariadne is a Python library for implementing GraphQL servers using schema-first approach. It supports both synchronous and asynchronous query execution, ships with batteries included for common GraphQL server problems like query cost validation or performance tracing and has simple API that is easy to extend or replace.

README

Ariadne can be installed with pip:

```
$ pip install ariadne
```

Minimal “Hello world” server example:

```
from ariadne import ObjectType, gql, make_executable_schema
from ariadne.asgi import GraphQL
 
type_defs = gql(
    """
    type Query {
        hello: String!
    }
    """
)
 
query_type = ObjectType("Query")
 
@query_type.field("hello")
def resolve_hello(*_):
    return "Hello world!"
 
schema = make_executable_schema(type_defs, query_type)
 
app = GraphQL(schema, debug=True)
```

Run the server with uvicorn:

```
$ pip install uvicorn
$ uvicorn example:app
```[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Package for easy building a GraphQL API with basic CRUD operations for Django models.

README

A Quickstart for Django Graphbox:

1. Install the package:

```
pip install django-graphbox
```

2. Create a new Django project:

```
django-admin startproject myproject
```

3. Create a new Django app:

```
cd myproject
python manage.py startapp myapp
```

4. Define your Django models in `myapp/models.py`:

```
from django.db import models
 
class MyModel(models.Model):
    name = models.CharField(max_length=100)
```

5. Create and run migrations:

```
python manage.py makemigrations
python manage.py migrate
```

6. Configure and Build your GraphQL Schema in `myapp/schema.py`:

```
from django_graphbox.builder import SchemaBuilder
from myapp.models import MyModel
 
builder = SchemaBuilder()
builder.add_model(MyModel)
 
query_class = builder.build_schema_query()
mutation_class = builder.build_schema_mutation()
```

7. Create a main Schema in `myproject/schema.py` (In this main schema you can add your own queries and mutations):

```
import graphene
from myapp.schema import query_class, mutation_class
 
class Query(query_class, graphene.ObjectType):
    pass
 
class Mutation(mutation_class, graphene.ObjectType):
    pass
 
schema = graphene.Schema(query=Query, mutation=Mutation)
```

8. Add the GraphQL view to your `myproject/urls.py`:

```
from django.urls import path
from graphene_file_upload.django import FileUploadGraphQLView
from django.views.decorators.csrf import csrf_exempt
from myproject.schema import schema
 
urlpatterns = [
    path('graphql/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True, schema=schema))),
]
```

9. Run the server:

```
python manage.py runserver
```

10. Open the GraphiQL interface at `http://localhost:8000/graphql` and start querying your API!

You can find advanced examples with authentication, filters, validations and more on GitHub or pypi.[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Turn your Django-models into a complete GraphQL API with all CRUD operations

README

You can install the package with pip

```
pip install graphene-django-cruddals
```

To use it, simply create a new class that inherits “ `DjangoModelCruddals` ” Suppose we have the following models.

```
from django.db import models
 
 
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    is_active = models.BooleanField(default=True)
```

Then we can create a complete CRUD+DALS for the models `Question` with the following code

```
from graphene_django_cruddals import DjangoModelCruddals
 
class CruddalsQuestion(DjangoModelCruddals):
    class Meta:
        model = Question
```

Now you can use the `schema` that was generated for you,

```
schema = CruddalsQuestion.Schema
```

or use in your existing schema root `Query` and `Mutation`

```
class Query(
    # ... your others queries
    CruddalsQuestion.Query,
    graphene.ObjectType,
):
    pass
 
 
class Mutation(
    # ... your others mutations
    CruddalsQuestion.Mutation,
    graphene.ObjectType,
):
    pass
 
 
schema = graphene.Schema( query=Query, mutation=Mutation, )
```

That’s it! You can test in graphiql or any other client that you use to test your GraphQL APIs..

Find more information in the [official documentation](https://graphene-django-cruddals.readthedocs.io/en/latest/).[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Python library for building GraphQL APIs.

README

To run a Graphene hello world script:

```
pip install graphene
```

Then run `python hello.py` with this code in `hello.py`:

```
import graphene
 
class Query(graphene.ObjectType):
  hello = graphene.String(name=graphene.String(default_value="World"))
 
  def resolve_hello(self, info, name):
    return 'Hello ' + name
 
schema = graphene.Schema(query=Query)
result = schema.execute('{ hello }')
print(result.data['hello']) # "Hello World"
```

There are also nice bindings for [Relay](https://facebook.github.io/relay/), Django, SQLAlchemy, and Google App Engine.[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Strawberry is a Python library for implementing code first GraphQL servers using modern Python features like type hints.

README

Here’s an example of a Strawberry hello world, first install the library:

```
pip install strawberry-graphql
```

Create an `app.py` file with this content:

```
import strawberry
 
@strawberry.type
class Query:
    @strawberry.field
    def hello(self, name: str = "World") -> str:
        return f"Hello {name}"
 
schema = strawberry.Schema(query=Query)
```

Then run `strawberry server app` and you will have a basic schema server running on `http://localhost:8000`.

Strawberry also has views for ASGI, Flask and Django and provides utilities like dataloaders and tracing.[Python](https://graphql.org/community/tools-and-libraries/?tags=python)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Python 3.6+ *(asyncio)* library for building GraphQL APIs.

README

To run a tartiflette hello world script:

```
pip install tartiflette
```

Then run `python hello.py` with this code in `hello.py`:

```
import asyncio
from tartiflette import Engine, Resolver
@Resolver("Query.hello")
async def resolver_hello(parent, args, ctx, info):
    return "hello " + args["name"]
async def run():
    tftt_engine = Engine("""
    type Query {
        hello(name: String): String
    }
    """)
    result = await tftt_engine.execute(
        query='query { hello(name: "Chuck") }'
    )
    print(result)
    # {'data': {'hello': 'hello Chuck'}}
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
```

There is also a nice [HTTP wrapper](https://github.com/dailymotion/tartiflette-aiohttp).[R](https://graphql.org/community/tools-and-libraries/?tags=r)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

General purpose GraphQL R client[Ruby](https://graphql.org/community/tools-and-libraries/?tags=ruby)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A high performance web server with support for GraphQL. Agoo strives for a simple, easy to use API for GraphQL.

README

```
require 'agoo'
 
class Query
  def hello
    'hello'
  end
end
 
class Schema
  attr_reader :query
 
  def initialize
    @query = Query.new()
  end
end
 
Agoo::Server.init(6464, 'root', thread_count: 1, graphql: '/graphql')
Agoo::Server.start()
Agoo::GraphQL.schema(Schema.new) {
  Agoo::GraphQL.load(%^type Query { hello: String }^)
}
sleep
 
# To run this GraphQL example type the following then go to a browser and enter
# a URL of localhost:6464/graphql?query={hello}
#
# ruby hello.rb
```[Ruby](https://graphql.org/community/tools-and-libraries/?tags=ruby)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Ruby library for building GraphQL APIs.

README

To run a hello world script with `graphql-ruby`:

```
gem install graphql
```

Then run `ruby hello.rb` with this code in `hello.rb`:

```
require 'graphql'
 
class QueryType < GraphQL::Schema::Object
  field :hello, String
 
  def hello
    "Hello world!"
  end
end
 
class Schema < GraphQL::Schema
  query QueryType
end
 
puts Schema.execute('{ hello }').to_json
```

There are also nice bindings for Relay and Rails.[Ruby](https://graphql.org/community/tools-and-libraries/?tags=ruby)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Fresh new GraphQL server for Rails applications, with a focus on natural and Ruby-like DSL

README

```
require 'rails-graphql'
 
class GraphQL::AppSchema < GraphQL::Schema
  query_fields do
    field(:hello).resolve { 'Hello World!' }
  end
end
 
puts GraphQL::AppSchema.execute('{ hello }')
```

Less is more! Please check it out the [docs](https://www.rails-graphql.dev/?utm_source=graphql_org).[Rust](https://graphql.org/community/tools-and-libraries/?tags=rust)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

A bring your own types GraphQL client for Rust

README

A client library for rust that generates queries from types you provide, verifying that the types match the shape of your schema.

It provides [a generator](https://generator.cynic-rs.dev/) to bootstrap types from existing GraphQL queries.

Usage example:

```
#[derive(cynic::QueryFragment, Debug)]
#[cynic(
    schema_path = "../schemas/starwars.schema.graphql",
    query_module = "query_dsl",
    graphql_type = "Root",
    argument_struct = "FilmArguments"
)]
struct FilmDirectorQuery {
    #[arguments(id = &args.id)]
    film: Option<Film>,
}
 
#[derive(cynic::QueryFragment, Debug)]
#[cynic(
    schema_path = "../schemas/starwars.schema.graphql",
    query_module = "query_dsl",
    graphql_type = "Film"
)]
struct Film {
    title: Option<String>,
    director: Option<String>,
}
 
#[derive(cynic::FragmentArguments)]
struct FilmArguments {
    id: Option<cynic::Id>,
}
 
fn main() {
    use cynic::{QueryBuilder, http::ReqwestBlockingExt};
 
    let query = FilmDirectorQuery::build(&FilmArguments {
        id: Some("ZmlsbXM6MQ==".into()),
    })
 
    reqwest::blocking::Client::new()
        .post("https://swapi-graphql.netlify.com/.netlify/functions/index")
        .run_graphql(query)
        .unwrap()
}
 
mod query_dsl {
    cynic::query_dsl!("../schemas/starwars.schema.graphql");
}
```[Rust](https://graphql.org/community/tools-and-libraries/?tags=rust)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Minimal GraphQL client for Rust

README

Usage example

```
use gql_client::Client;
 
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
  let endpoint = "https://graphqlzero.almansi.me/api";
  let query = r#"
    query AllPostsQuery {
      posts {
        data {
          id
        }
      }
    }
  "#;
 
  let client = Client::new(endpoint);
  let data: AllPosts = client.query::<AllPosts>(query).await.unwrap();
 
  println!("{:?}" data);
 
  Ok(())
}
```[Rust](https://graphql.org/community/tools-and-libraries/?tags=rust)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Async-graphql is a high-performance server-side library that supports all GraphQL specifications.

README

```
use async_graphql::*;
struct Query;
#[Object]
impl Query {
   /// Returns the sum of a and b
   async fn add(&self, a: i32, b: i32) -> i32 {
       a + b
   }
}
```[Rust](https://graphql.org/community/tools-and-libraries/?tags=rust)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

GraphQL server library for Rust[Scala](https://graphql.org/community/tools-and-libraries/?tags=scala)

[

Client

](https://graphql.org/community/tools-and-libraries/?tags=client)

Caliban is a functional library for building GraphQL servers and clients in Scala. It offers with client code generation and type-safe queries.

README

An example of defining a GraphQL query and running it with `caliban`:

```
// define your query using Scala
val query: SelectionBuilder[RootQuery, List[CharacterView]] =
  Query.characters {
    (Character.name ~ Character.nicknames ~ Character.origin)
      .mapN(CharacterView)
  }
 
import sttp.client3._
// run the query and get the result already parsed into a case class
val result = query.toRequest(uri"http://someUrl").send(HttpClientSyncBackend()).body
```[Scala](https://graphql.org/community/tools-and-libraries/?tags=scala)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

Caliban is a functional library for building GraphQL servers and clients in Scala. It offers minimal boilerplate and excellent interoperability.

README

An example of a simple GraphQL schema and query with `caliban`:

```
import caliban._
import caliban.schema.Schema.auto._
 
// schema
case class Query(hello: String)
 
// resolver
val resolver = RootResolver(Query("Hello world!"))
 
val api = graphQL(resolver)
 
for {
  interpreter <- api.interpreter
  result      <- interpreter.execute("{ hello }")
} yield result
```[Scala](https://graphql.org/community/tools-and-libraries/?tags=scala)

[

Server

](https://graphql.org/community/tools-and-libraries/?tags=server)

A Scala GraphQL library that supports [Relay](https://facebook.github.io/relay/).

README

An example of a hello world GraphQL schema and query with `sangria`:

```
import sangria.schema._
import sangria.execution._
import sangria.macros._
 
val QueryType = ObjectType("Query", fields[Unit, Unit](
  Field("hello", StringType, resolve = _ ⇒ "Hello world!")
))
 
val schema = Schema(QueryType)
 
val query = graphql"{ hello }"
 
Executor.execute(schema, query) map println
```

A GraphQL client for iOS that returns results as query-specific Swift types, and integrates with Xcode to show your Swift source and GraphQL side by side, with inline validation errors.

A Tool for Writing Declarative, Type-Safe and Data-Driven Applications in SwiftUI using GraphQL and Apollo

An Objective-C GraphQL client for iOS.

A GraphQL client that lets you forget about GraphQL.

README

SwiftGraphQL is a Swift code generator and a lightweight GraphQL client. It lets you create queries using Swift, and guarantees that every query you create is valid.

The library is centered around three core principles:

🚀 If your project compiles, your queries work. 🦉 Use Swift in favour of GraphQL wherever possible. 🌳 Your application model should be independent of your schema.

Here’s a short preview of the SwiftGraphQL code

```
import SwiftGraphQL
 
// Define a Swift model.
struct Human: Identifiable {
    let id: String
    let name: String
    let homePlanet: String?
}
 
// Create a selection.
let human = Selection.Human {
    Human(
        id: try $0.id(),
        name: try $0.name(),
        homePlanet: try $0.homePlanet()
    )
}
 
// Construct a query.
let query = Selection.Query {
    try $0.humans(human.list)
}
 
// Perform the query.
send(query, to: "http://swift-graphql.heroku.com") { result in
    if let data = try? result.get() {
        print(data) // [Human]
    }
}
```

Swift library for building GraphQL schemas/types fast, safely and easily.

Swift library for writing Declarative, Type-Safe GraphQL APIs with Zero Boilerplate.

A configurable, high-performance routing runtime for Apollo Federation

README

**Apollo Router Core**

The **Apollo Router Core** is a configurable, high-performance **graph router** written in Rust to run a [federated supergraph](https://www.apollographql.com/docs/federation/) that uses [Apollo Federation 2](https://www.apollographql.com/docs/federation/v2/federation-2/new-in-federation-2).

Apollo Router Core is free, source-available, well-tested, regularly benchmarked, includes most major features of Apollo Gateway and is able to serve production-scale workloads.

**GraphOS Router**

In conjunction with the [Apollo GraphOS platform](https://www.apollographql.com/docs/graphos/platform), GraphOS Router is the enterprise-grade runtime plane and a client’s entry point to your federated supergraph. Configure it to secure your supergraph, monitor and optimize performance, extend functionality, and more.

An open-source GraphQL gateway with first-class, built-in support for both the GraphQL Composite Schemas specification and Apollo Federation.

README

[Fusion](https://chillicream.com/docs/fusion/?utm_source=graphql_org&utm_medium=referral) is an open-source GraphQL gateway that lets you split one GraphQL API into multiple smaller services without changing how clients consume it.

Fusion supports two federation protocols as first-class citizens: the [GraphQL Composite Schemas specification](https://github.com/graphql/composite-schemas-spec), an open standard developed under the GraphQL Foundation, and [Apollo Federation](https://chillicream.com/docs/fusion/connectors/apollofederation/?utm_source=graphql_org&utm_medium=referral). Both are built into the gateway core, so existing Apollo Federation v2 subgraphs run without modification, and subgraphs of both flavors can be composed into a single graph.[Tools](https://graphql.org/community/tools-and-libraries/?tags=tools)

[

General

](https://graphql.org/community/tools-and-libraries/?tags=general)

Build and execute GraphQL queries in the terminal.

README

Run `gqt` against your GraphQL endpoint. Build your query in an intuitive TUI and execute it. The response from the server is written to standard output.

```
gqt -e https://your.app.com/graphql
```[Tools](https://graphql.org/community/tools-and-libraries/?tags=tools)

[

General

](https://graphql.org/community/tools-and-libraries/?tags=general)

GraphQL code generator with flexible support for custom plugins and templates like Typescript (frontend and backend), React Hooks, resolvers signatures and more.[Tools](https://graphql.org/community/tools-and-libraries/?tags=tools)

[

General

](https://graphql.org/community/tools-and-libraries/?tags=general)

GraphQL Protect is a GraphQL Protect is dead-simple yet highly customizable security proxy compatible with any HTTP GraphQL Server or Gateway.

README

[GraphQL Protect](https://github.com/ldebruijn/graphql-protect) helps you protect your GraphQL API against abuse by providing a large number of plug-and-play protection mechanism with sane defaults, while still allowing you complete customizability.

Getting started with GraphQL Protect is as simple as pulling the provided container, or running the binary directly, and supplying it with your configuration.

GraphQL Protect offers the following protection mechanism, and more:

1. **Trusted Documents** (Persisted Operations)
2. **Max Aliases**
3. **Max Tokens**
4. **Max Depth**
5. **Max Batch**
6. **Block Field Suggestions**
7. **Obfuscate upstream errors**
8. **Enforce POST**
9. **Access Logging**
10. [… and more!](https://github.com/ldebruijn/graphql-protect?tab=readme-ov-file#features)

Protecting your GraphQL API against abuse has never been easier, start protecting your API today.

The full [example can be found on GitHub](https://github.com/ldebruijn/graphql-protect?tab=readme-ov-file#installation).

Hive Gateway can act as a GraphQL federation gateway or a proxy for any GraphQL service.

README

[Hive Gateway](https://the-guild.dev/graphql/hive/docs/gateway) is a fully open-source, MIT-licensed GraphQL router that can act as a [GraphQL Federation](https://the-guild.dev/graphql/hive/federation) gateway, a subgraph or a proxy gateway for any GraphQL API service.

Hive Gateway provides a flexible, open-source solution tailored to meet the needs of modern GraphQL architectures.

It supports deployment as a [standalone binary](https://the-guild.dev/graphql/hive/docs/gateway#starting-the-gateway), a [Docker image](https://the-guild.dev/graphql/hive/docs/gateway/deployment/docker), or a [JavaScript package](https://the-guild.dev/graphql/hive/docs/gateway#installation), making it compatible with environments such as [Node.js](https://the-guild.dev/graphql/hive/docs/gateway/deployment/runtimes/nodejs), [Bun](https://the-guild.dev/graphql/hive/docs/gateway/deployment/runtimes/bun), [Deno](https://the-guild.dev/graphql/hive/docs/gateway/deployment/runtimes/deno), [Google Cloud Functions](https://the-guild.dev/graphql/hive/docs/gateway/deployment/serverless/google-cloud-platform), [Azure Functions](https://the-guild.dev/graphql/hive/docs/gateway/deployment/serverless/azure-functions), [AWS Lambda](https://the-guild.dev/graphql/hive/docs/gateway/deployment/serverless/aws-lambda), or [Cloudflare Workers](https://the-guild.dev/graphql/hive/docs/gateway/deployment/serverless/cloudflare-workers).[Tools](https://graphql.org/community/tools-and-libraries/?tags=tools)

[

General

](https://graphql.org/community/tools-and-libraries/?tags=general)

Open source Kubernetes-native tool for API Mocking and Testing

README

Microcks is a platform for turning your API and microservices assets - *GraphQL schemas*, *OpenAPI specs*, *AsyncAPI specs*, *gRPC protobuf*, *Postman collections*, *SoapUI projects* \_ - into live simulations in seconds.

It also reuses these assets for running compliance and non-regression tests against your API implementation. We provide integrations with *Jenkins*, *GitHub Actions*, *Tekton* and many others through a simple CLI.[Tools](https://graphql.org/community/tools-and-libraries/?tags=tools)

[

General

](https://graphql.org/community/tools-and-libraries/?tags=general)

Generate types for GraphQL queries in TypeScript, Swift, golang, C#, C++, and more.[Tools](https://graphql.org/community/tools-and-libraries/?tags=tools)

[

General

](https://graphql.org/community/tools-and-libraries/?tags=general)

A modern API testing tool for web applications built with Open API and GraphQL specifications.

README

Run Schemathesis via Docker against your GraphQL endpoint:

```
docker run schemathesis/schemathesis \
  run https://your.app.com/graphql
```

Schemathesis will generate queries matching your GraphQL schema and catch server crashes automatically. Generated queries have arbitrary depth and may contain any subset of GraphQL types defined in the input schema. They expose edge cases in your code that are unlikely to be found otherwise.

Note that you can write your app in any programming language; the tool will communicate with it over HTTP.

For example, running the command above against `https://bahnql.herokuapp.com/graphql` uncovers that running the `{ search(searchTerm: "") { stations { name } } }` query leads to a server error:

```
{
  "errors": [
    {
      "message": "Cannot read property 'city' of undefined",
      "locations": [
        {
          "line": 1,
          "column": 28
        }
      ],
      "path": ["search", "stations"]
    }
  ],
  "data": null
}
```

Open-source, full lifecycle GraphQL federation and API management platform with schema registry, composition checks, routing, analytics, and distributed tracing

README

[WunderGraph Cosmo](https://wundergraph.com/cosmo) is an open-source GraphQL federation platform for managing and operating federated graphs at scale. It provides a schema registry, composition and breaking-change checks, a high-performance router, analytics, tracing, access control, and support for GraphQL Federation v1 and v2.

Cosmo supports both federated and monolithic GraphQL APIs and can run locally, fully on‑premises, or in the cloud as a managed service. The platform includes a CLI, control plane, router, and Studio to handle composition, routing, analytics, and governance for GraphQL architectures.

Cosmo also supports integrating non‑GraphQL backends through Cosmo Connect, which lets teams use GraphQL Federation without requiring backend teams to run GraphQL servers. Connect offers Router Plugins (local processes managed by the router) and independently deployed gRPC Services in any supported language to bring external APIs and services into a federated graph.

To get started, see the [Cosmo overview](https://cosmo-docs.wundergraph.com/overview) and the [GitHub repository](https://github.com/wundergraph/cosmo).