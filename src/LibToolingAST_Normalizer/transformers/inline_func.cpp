#ifndef CLANG_LIBS
#define CLANG_LIBS

#include "llvm/Support/CommandLine.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#endif

#include "utils_transform.h"
#include "../Utilities/Utils.h"
#include "ASTFrontendActionTemplate.inl"
#include "ControlDataFlow/ControlFlowGraphWithDataFlow.h"
#include "ControlDataFlow/CDFGraphQueryHandler.h"
#include "include/SourceTextHelper.h"
#include<string>

static llvm::cl::OptionCategory MyOptionCategory("Inline-User-Defined-Function Transformer");
static llvm::cl::opt<int> OurCMDOption1("seed", llvm::cl::cat(MyOptionCategory));

using namespace clang;


class InlineTransformer : public RecursiveASTVisitor<InlineTransformer> {
public:

    ControlFlowGraphWithDataFlow *cfggraph;

    explicit InlineTransformer(ASTContext &Context, Rewriter &InlineRewriter) : Context(Context),
                                                                                 InlineRewriter(InlineRewriter),
                                                                              sm(Context.getSourceManager()) {
        cfggraph = new ControlFlowGraphWithDataFlow(&Context);
    }

    ~InlineTransformer() {
        delete cfggraph;
    }
    std::string funcName = "";
    /**
  * Visit all functions.
  * @param f
  * @return
  */
    bool VisitFunctionDecl(FunctionDecl *f) {
//        bool inmainfile = sm.isInMainFile(f->getLocation());
//        if (inmainfile) {
//            cfggraph->addFunctionDecl(f);
//            this->fctdecls.push_back(f);
//        }
        funcName = f->getNameInfo().getName().getAsString();
//        if (funcName == "g") {
//            llvm::errs() << "** Rewrote function def: " << funcName << "\n";
//        }
        return true;
    }

    bool VisitCallExpr(CallExpr *call) {
//        rewriter.ReplaceText(call->getLocStart(), 7, "add5");
//        errs() << "** Rewrote function call\n";
//        if (sm.isWrittenInMainFile(d->getLocStart()))
        if (call != NULL && sm.isWrittenInMainFile(call->getLocStart())){
            QualType q = call->getType();
            const Type *t = q.getTypePtrOrNull();

            if(t != NULL)
            {
                FunctionDecl *func = call->getDirectCallee(); //gives you callee function

                if (func)
                // If this is the function we are looking for
//                if (func->isMain()) {
//                    // Grab the source location (FullSourceLoc = SourceLocation + SourceManager)
//                    FullSourceLoc FullLocation =
//                            Context.getFullLoc(call->getLocStart());
//
//                    if (FullLocation.isValid())
//                        llvm::outs() << "Found call at "
//                                     << FullLocation.getSpellingLineNumber() << ":"
//                                     << FullLocation.getSpellingColumnNumber() << "\n";
//                }

//                if (func->isexp)
                if (func->isDefined()) {
                    std::string callee = func->getNameInfo().getName().getAsString();
                    llvm::errs() << callee << " is called by " << funcName << "\n";
                }

//                if (const auto *Ref =
//                        dyn_cast<DeclRefExpr>(call->getCallee()->IgnoreImplicit())) {
//                    llvm::errs() << "callee: " << Ref->getNameInfo().getName().getAsString() << "\n";
//                }
            }
        }
        return true;
    }

    void replacecommand(int seed) {
        for (auto f : fctdecls) {
            llvm::errs() << "FuncName: " << f->getName() << "__" << f->isMain() << "\n";
        }
    }

private:
    ASTContext &Context;
    Rewriter &InlineRewriter;
    SourceManager &sm;

    std::vector<const FunctionDecl*> fctdecls;
};


class MyASTConsumer : public ASTConsumer {
public:

    explicit MyASTConsumer(ASTContext &Context, Rewriter &InlineRewriter) : Visitor(Context, InlineRewriter) {}

    void HandleTranslationUnit(ASTContext &Context) override {
        Visitor.TraverseDecl(Context.getTranslationUnitDecl());

        auto seed = static_cast<int>(OurCMDOption1.getValue());
        Visitor.replacecommand(seed);
    }

private:
    InlineTransformer Visitor;
};

int main(int argc, const char **argv) {
    clang::tooling::CommonOptionsParser OptionsParser(argc, argv, MyOptionCategory);
    clang::tooling::ClangTool Tool(OptionsParser.getCompilations(), OptionsParser.getSourcePathList());
    return Tool.run(&*clang::tooling::newFrontendActionFactory<MyFrontendAction<MyASTConsumer>>());
}

